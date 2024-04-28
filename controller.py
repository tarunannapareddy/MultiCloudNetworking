from flask import Flask, request, jsonify
import boto3
from routing import solve_shortest_path_problem

app = Flask(__name__)

# Dictionary to store registered nodes
registered_nodes = {}

# List to store registered attachments
registered_attachments = []

@app.route('/register_node', methods=['POST'])
def register_node():
    node_data = request.get_json()
    node_name = node_data.get('nodeName')
    if node_name in registered_nodes:
        return jsonify({'error': 'Node already registered'})
    registered_nodes[node_name] = {
        'vpcid': node_data.get('vpcid'),
        'vpcrange': node_data.get('vpcrange'),
        'tgwid': node_data.get('tgwid')
    }
    return jsonify({'message': 'Node registered successfully'})

@app.route('/register_attachment', methods=['POST'])
def register_attachment():
    attachment_data = request.get_json()
    src_node_name = attachment_data.get('srcNodeName')
    dst_node_name = attachment_data.get('dstNodeName')
    attachment_exists = False
    for attachment in registered_attachments:
        if attachment['srcNodeName'] == src_node_name and attachment['dstNodeName'] == dst_node_name:
            attachment_exists = True
            break
    if attachment_exists:
        return jsonify({'error': 'Attachment already registered'})
    registered_attachments.append(attachment_data)
    return jsonify({'message': 'Attachment registered successfully'})

@app.route('/add_work', methods=['POST'])
def add_work():
    work_data = request.get_json()
    src_node = work_data.get('srcNode')
    dst_node = work_data.get('dstNode')
    demand = work_data.get('demand')

    demands = {(src_node, dst_node): demand}

    routing_paths = solve_shortest_path_problem(registered_nodes, registered_attachments, demands)

    # Create Transit Gateway route entries based on the routing paths
    for src, dst, flow in routing_paths:
        src_node_details = registered_nodes[src]
        dst_node_details = registered_nodes[dst]
        tgw_id = src_node_details['tgwid']
        tgw_route_table_id = get_transit_gateway_route_table(tgw_id)

        # Find the attachment between src and dst nodes
        attachment = next((a for a in registered_attachments if a['srcNodeName'] == src and a['dstNodeName'] == dst), None)
        if attachment:
            peering_id = attachment['peeringId']
            create_transit_gateway_route_entry(tgw_route_table_id, dst_node_details['vpcrange'], peering_id)
        else:
            print(f"No attachment found between {src} and {dst}")

    return jsonify({'message': 'Work added successfully'})

def get_transit_gateway_route_table(transit_gateway_id):
    ec2_client = boto3.client('ec2',
                              aws_access_key_id='AKIAUTA4UV6WXGCJ4KVQ', 
                              aws_secret_access_key='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', 
                              region_name='ap-south-1')
    response = ec2_client.describe_transit_gateway_route_tables(
        Filters=[
            {
                'Name': 'transit-gateway-id',
                'Values': [transit_gateway_id]
            }
        ]
    )
    route_table_id = response['TransitGatewayRouteTables'][0]['TransitGatewayRouteTableId']
    return route_table_id

def create_transit_gateway_route_entry(tgw_route_table_id, destination_cidr, peering_id):
    ec2_client = boto3.client('ec2',
                              aws_access_key_id='AKIAUTA4UV6WXGCJ4KVQ', 
                              aws_secret_access_key='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', 
                              region_name='ap-south-1')
    
    ec2_client.create_transit_gateway_route(
        DestinationCidrBlock=destination_cidr,
        TransitGatewayRouteTableId=tgw_route_table_id,
        TransitGatewayAttachmentId=peering_id
    )

if __name__ == '__main__':
    app.run(debug=True)
