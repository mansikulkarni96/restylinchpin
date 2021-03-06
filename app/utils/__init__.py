import os
import json
from typing import List
import data_access_layer.RestDB
from response_messages import response
from flask import jsonify


def get_connection(db_path):
    """
        Method to create an object of subclass and create a connection
        :return : an instantiated object for class RestDB
    """
    return data_access_layer.RestDB.RestDB(db_path)


def create_fetch_cmd(data, identity, workspace_dir) -> List[str]:
    """
        Creates a list to feed the subprocess in fetch API
        :param data: JSON data from POST requestBody
        :param identity: unique uuid_name assigned to the workspace
        :return a list for the subprocess to run
    """
    url = data['url']
    repo = None
    # initial list
    cmd = ["linchpin", "-w " + workspace_dir + identity, "fetch"]

    # Check for repoType field in request,
    # Only true if it is set to web
    if 'repoType' in data:
        if data['repoType'] == 'web':
            repo = 'web'
            cmd.append("--web")

    if 'rootfolder' in data:
        cmd.extend(("--root", data['rootfolder']))

    if repo is None and 'branch' in data:
        cmd.extend(("--branch", data['branch']))

    # last item to be added in the array
    if 'url' in data:
        cmd.append(str(url))
    return cmd


def create_cmd_workspace(data, identity, action,
                         workspace_path, workspace_dir) -> List[str]:
    """
        Creates a list to feed the subprocess for provisioning/
        destroying existing workspaces
        :param data: JSON data from POST requestBody
        :param identity: unique uuid_name assigned to the workspace
        :param action: up or destroy action
        :return a list for the subprocess to run
    """
    if 'pinfile_path' in data:
        pinfile_path = data['pinfile_path']
        check_path = identity + pinfile_path
    else:
        check_path = identity
    cmd = ["linchpin", "-w " + workspace_dir + check_path]
    if 'pinfileName' in data:
        cmd.extend(("-p", data['pinfileName']))
        pinfile_name = data['pinfileName']
    else:
        pinfile_name = "PinFile"
    if not check_workspace_has_pinfile(check_path,
                                       pinfile_name, workspace_path):
        return jsonify(status=response.PINFILE_NOT_FOUND)
    cmd.append(action)
    if 'tx_id' in data:
        cmd.extend(("-t", data['tx_id']))
    elif 'run_id' and 'target' in data:
        cmd.extend(("-r", data['run_id'], data['target']))
    if 'inventory_format' in data:
        cmd.extend(("--if", data['inventory_format']))
    return cmd


def create_cmd_up_pinfile(data,
                          identity,
                          workspace_path,
                          workspace_dir,
                          pinfile_json_path) -> List[str]:
    """
        Creates a list to feed the subprocess for provisioning
        new workspaces instantiated using a pinfile
        :param data: JSON data from POST requestBody
        :param identity: unique uuid_name assigned to the workspace
        :return a list for the subprocess to run
    """
    pinfile_content = data['pinfile_content']
    json_pinfile_path = workspace_path + "/" + identity + pinfile_json_path
    with open(json_pinfile_path, 'w') as json_data:
        json.dump(pinfile_content, json_data)
    cmd = ["linchpin", "-w " + workspace_dir + identity + "/dummy", "-p" +
           "PinFile.json", "up"]
    if 'inventory_format' in data:
        cmd.extend(("--if", data['inventory_format']))
    return cmd


def check_workspace_has_pinfile(name, pinfile_name, workspace_path) -> bool:
    """
        Verifies if a workspace to be provisioned contains a PinFile.json
        :param name: name of the workspace to be verified
        :param pinfile_name: name of pinfile in directory
        :return a boolean value True or False
    """
    return os.listdir(workspace_path + "/" + name).__contains__(pinfile_name)


def check_workspace_empty(name, workspace_path) -> bool:
    """
        Verifies if a workspace fetched/created is empty
        :param name: name of the workspace to be verified
        :return a boolean value True or False
    """
    return os.listdir(workspace_path + "/" + name) == []
