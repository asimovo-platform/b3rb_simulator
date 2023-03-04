from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions.path_join_substitution import PathJoinSubstitution

from launch_ros.actions import Node

ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('robot_name', default_value='mrbuggy3',
                          description='Robot name'),
    DeclareLaunchArgument('world', default_value='depot',
                          description='World name'),
    DeclareLaunchArgument('model', default_value='standard',
                          choices=['standard', 'lite'],
                          description='MR Buggy3 Model'),
]


def generate_launch_description():
    namespace = LaunchConfiguration('robot_name')
    use_sim_time = LaunchConfiguration('use_sim_time')

    pkg_mrbuggy3_gz_bringup = get_package_share_directory(
        'mrbuggy3_gz_bringup')

    mrbuggy3_ros_gz_bridge_launch = PathJoinSubstitution(
        [pkg_mrbuggy3_gz_bringup, 'launch', 'ros_gz_bridge_base.launch.py'])

    base_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([mrbuggy3_ros_gz_bridge_launch]),
        launch_arguments=[
            ('robot_name', LaunchConfiguration('robot_name')),
            ('world', LaunchConfiguration('world'))
        ]
    )

    # lidar bridge
    lidar_bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        namespace=namespace,
        name='lidar_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        arguments=[
            ['/world/', LaunchConfiguration('world'),
             '/model/', LaunchConfiguration('robot_name'),
             '/link/rplidar_link/sensor/rplidar/scan' +
             '@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan']
        ],
        remappings=[
            (['/world/', LaunchConfiguration('world'),
              '/model/', LaunchConfiguration('robot_name'),
              '/link/rplidar_link/sensor/rplidar/scan'],
             '/scan')
        ],
        condition=LaunchConfigurationEquals('model', 'lidar'))

    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(ros_gz_bridge)
    ld.add_action(lidar_bridge)
    return ld
