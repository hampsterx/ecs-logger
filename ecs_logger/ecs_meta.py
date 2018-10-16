import os
import logging
import requests
import time
import json

from requests import exceptions

log = logging.getLogger(__name__)

def format_data(ecs_info=None, cloud_info=None):

    data = {}

    if ecs_info:
        data.update({
            'cloud.provider': 'ec2',
            'cloud.availability_zone': cloud_info.get('availabilityZone', None),
            'cloud.region': cloud_info.get('region', None),
            'cloud.instance.id': cloud_info.get('instanceId', None),
            'cloud.machine.type': cloud_info.get('instanceType', None),
            'cloud.instance.ip': cloud_info.get('privateIp', None)
        })

    if cloud_info:
        data.update({
            'cloud.cluster': ecs_info.get('Cluster', None),
            'container.id': ecs_info.get('ContainerID', None),
            'container.image.name': ecs_info.get('ImageID', None),
            'container.name': ecs_info.get('ContainerName', None),
            'service.name': ecs_info.get('TaskDefinitionFamily', None),
            'service.version': ecs_info.get('TaskDefinitionRevision', None)
        })

    return data

def read_ecs_meta(attempt=1, max_attempts=3, wait_s=1, es_meta_wait_s=3):

    meta_file_path = os.environ.get('ECS_CONTAINER_METADATA_FILE', None)

    # Not on EC2
    if not meta_file_path:
        return format_data()

    time.sleep(wait_s)

    if attempt > max_attempts:
        log.info("Timed out trying to fetch ECS Container Metadata")
        return format_data()

    with open(meta_file_path, 'r') as f:
        contents = f.read()
        if not contents:
            return read_ecs_meta(attempt=attempt + 1)

        ecs_info = json.loads(contents)

        if ecs_info['MetadataFileStatus'] != "READY":
            return read_ecs_meta(attempt=attempt + 1)

        try:
            cloud_info = requests.get("http://169.254.169.254/latest/dynamic/instance-identity/document", timeout=es_meta_wait_s).json()
        except exceptions.HTTPError:
            cloud_info = None
            log.error("Failed to fetch ecs_meta")


    return format_data(ecs_info=ecs_info, cloud_info=cloud_info)
