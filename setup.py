from setuptools import setup

package_name = 'tf2_to_pose'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Diego Cubillo',
    maintainer_email='dcubillo@comillas.edu',
    description='Transform listener that publishes the pose of a frame respect to another frame',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tf2_to_pose = tf2_to_pose.tf2_to_pose:main',
        ],
    },
)
