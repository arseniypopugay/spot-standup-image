import os
import robonomicsinterface as RI
import requests
import time
from spot_controller import SpotController

ROBOT_IP = "192.168.80.3"#os.environ['ROBOT_IP']
SPOT_USERNAME = "admin"#os.environ['SPOT_USERNAME']
SPOT_PASSWORD = "2zqa8dgw7lor"#os.environ['SPOT_PASSWORD']

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

    # Use wrapper in context manager to lease control, turn on E-Stop, power on robot and stand up at start
    # and to return lease + sit down at the end
    with SpotController(username=SPOT_USERNAME, password=SPOT_PASSWORD, robot_ip=ROBOT_IP) as spot:

        time.sleep(2)

        # Move head to specified positions with intermediate time.sleep
        spot.move_head_in_points(yaws=[0.2, 0],
                                 pitches=[0.3, 0],
                                 rolls=[0.4, 0],
                                 sleep_after_point_reached=1)
        time.sleep(3)

        # Make Spot to move by goal_x meters forward and goal_y meters left
        spot.move_to_goal(goal_x=0.5, goal_y=0)
        time.sleep(3)

        # Control Spot by velocity in m/s (or in rad/s for rotation)
        spot.move_by_velocity_control(v_x=-0.3, v_y=0, v_rot=0, cmd_duration=2)
        time.sleep(3)
    exit(0)

def launch_robonomics_subsciber():
    # Connect to Robonomic's RPC node
    interface = RI.Account(remote_ws="wss://kusama.rpc.robonomics.network")
    print("Robonomics subscriber starting...")

    # Start subscriber to listen to any new Launch send to listening account
    subscriber = RI.Subscriber(interface, RI.SubEvent.NewLaunch, robonomics_transaction_callback,
                               ROBONOMICS_LISTEN_ROBOT_ACCOUNT)


if __name__=='__main__':
    launch_robonomics_subsciber()
