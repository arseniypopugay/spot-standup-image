import os
import robonomicsinterface as RI
import requests


# Get account where launch would be sent and IPFS gateway where metadata is stored
ROBONOMICS_LISTEN_ROBOT_ACCOUNT = os.environ.get("ROBONOMICS_LISTEN_ROBOT_ACCOUNT")
IPFS_COMMAND_GATEWAY = os.getenv('IPFS_COMMAND_GATEWAY')


def robonomics_transaction_callback(data, launch_event_id):
    # Receive sender, recipient and metadata
    sender, recipient, command_params_32_bytes = data

    # Convert metadata to IPFS hash
    command_params_ipfs_hash = RI.ipfs_32_bytes_to_qm_hash(command_params_32_bytes)

    # Receive json with data from IPFS Gateway
    message = requests.get(f'{IPFS_COMMAND_GATEWAY}/{command_params_ipfs_hash}').json()

    print('Got message from', sender)
    print('launch id', launch_event_id)
    print(message)


def launch_robonomics_subsciber():
    # Connect to Robonomic's RPC node
    interface = RI.Account(remote_ws="wss://kusama.rpc.robonomics.network")
    print("Robonomics subscriber starting...")

    # Start subscriber to listen to any new Launch send to listening account
    subscriber = RI.Subscriber(interface, RI.SubEvent.NewLaunch, robonomics_transaction_callback,
                               ROBONOMICS_LISTEN_ROBOT_ACCOUNT)


if __name__=='__main__':
    launch_robonomics_subsciber()
    
