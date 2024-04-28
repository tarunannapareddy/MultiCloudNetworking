# Multi-Cloud Networking

This is a project that aims to provide a solution for traffic engineering in a multi-cloud networking environment. The project includes a Flask application that handles registration of nodes and attachments, as well as adding work (demands) between nodes. Additionally, it includes a routing module that solves the shortest path problem using the PuLP library.

## Prerequisites

- Python 3
- Flask
- PuLP
- boto3 (AWS Python SDK)
- Access to AWS cloud account

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages by running the following command:

## Usage

1. Start the Flask application by running the following command:
```
python3 main.py
```
2. Register nodes using the `/register_node` endpoint. For example:
``` 
http://localhost:5000/register_node 
{
    "nodeName": "node1",
    "vpcid": "vpc-0380cb784d683fe54",
    "vpcrange": "10.80.0.0/16",
    "tgwid": "tgw-0dd807e3232367b54"
}
```
3. Register attachments (connections) between nodes using the `/register_attachment` endpoint. For example:
```   
http://localhost:5000/register_attachment
{
    "srcNodeName": "node1",
    "dstNodeName": "node2",
    "capacity": 100,
    "peeringId": "tgw-attach-059377b34d5e86699"
}
``` 
5. Add work (demands) between nodes using the `/add_work` endpoint. For example:
``` 
http://localhost:5000/add_work
{
    "srcNode": "node1",
    "dstNode": "node2",
    "demand": 50
}
``` 
The application will then solve the shortest path problem and create the necessary Transit Gateway route entries based on the routing paths.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.
