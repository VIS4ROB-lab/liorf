import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():

    share_dir = get_package_share_directory('liorf')
    rviz_config_file = os.path.join(share_dir, 'rviz', 'mapping.rviz')

    rviz_use = LaunchConfiguration('rviz')
    parameter_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    params_declare = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            share_dir, 'config', 'lio_sam_default.yaml'),
        description='FPath to the ROS2 parameters file to use.')
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz to monitor results'
    )

    return LaunchDescription([
        params_declare,
        declare_use_sim_time_cmd,
        declare_rviz_cmd,
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments='0.0 0.0 0.0 0.0 0.0 0.0 map odom'.split(' '),
            parameters=[parameter_file],
            output='screen'
        ),
        Node(
            package='liorf',
            executable='liorf_imuPreintegration',
            name='liorf_imuPreintegration',
            parameters=[parameter_file, 
                    {'use_sim_time': use_sim_time}],
            output='screen',
            prefix=['nice -n 20']
        ),
        Node(
            package='liorf',
            executable='liorf_imageProjection',
            name='liorf_imageProjection',
            parameters=[parameter_file, 
                    {'use_sim_time': use_sim_time}],
            output='screen',
            prefix=['nice -n 20']
        ),
        Node(
            package='liorf',
            executable='liorf_mapOptmization',
            name='liorf_mapOptmization',
            parameters=[parameter_file, 
                    {'use_sim_time': use_sim_time}],
            output='screen',
            prefix=['nice -n 20']
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_file],
            output='screen',
            condition=IfCondition(rviz_use)
        )
    ])