#!/usr/bin/python3
#-*- coding: UTF-8 -*-


import os
import json
import requests


def print_greeting_msg():
    print("\nWelcome to Aviatrix Transit-Network API with Python!")
    print("Aviatrix  --> Encrypted Tunnel  --> ∧v!@+r!x")
    print("✈ ☁ ✈ Aviatrix ✈ ☁ ✈ The Best Cloud Network Architect!! ✈ ☁ ✈ Aviatrix ✈ ☁ ✈")
    return



def read_config_file(path_to_file):
    with open(path_to_file, "r") as in_file_stream:
        config = json.load(in_file_stream)
        return config



def login(url=None, username=None, password=None):
    """
    This function logs user onto the Aviatrix controller and return CID (session)
    :param url: "https"//CONTROLLER_IP/v1/api
    :param username: Aviatrix-Cloud-Account username
    :param password: password
    :return: CID
    """
    data = {
        "action": "login",
        "username": username,
        "password": password
    }

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    if res_dict["return"]:
        CID = res_dict["CID"]
        return CID
    else:
        print(res_dict)
        print("ERROR: Login failed. Please check your password or configurations and retry.")
        os.system("pause")

    return



def get_controller_version(url, CID):
    params = {
        "action": "list_version_info",
        "CID": CID
    }
    response = requests.get(url=url, params=params, verify=False)
    res_dict = response.json()
    return res_dict



def check_requirements(config):
    ##### Check controller login
    print("    Checking Aviatrix controller accessibility... ")

    ### Login and Get CID
    controller_ip = config["controller"]["public_ip"]
    url = "https://" + controller_ip + "/v1/api"
    admin_password = config["controller"]["admin_password"]
    CID = login(url=url, username="admin", password=admin_password)

    print("        PASS: Successfully logged onto controller!")


    ### Check controller version
    print("    Checking Aviatrix controller version... ")

    # Get controller current version
    versions = ["UserConnect-3.1", "UserConnect-3.2", "UserConnect-3.3"]
    res_dict = get_controller_version(url=url, CID=CID)
    current_version = res_dict["results"]["current_version"]
    is_valid = False

    # Check version list
    for version in versions:
        if version in current_version:
            is_valid = True

    if is_valid:
        print("        PASS: Good! controller version is: " + current_version)
    else:
        print("        Fail: Current controller version is: " + current_version)
        print("        Please upgrade controller to the version that supports Transit Network Solution.")
        os.system("pause")


    ### Check cloud-account
    pass

    return True



def list_transit_gw_supported_sizes(url=None, CID=None):
    """
    This function invokes Aviatrix API "list_transit_gw_supported_sizes" and return a list of sizes (string)
    """
    sizes = list()
    params = {
        "action": "list_transit_gw_supported_sizes",
        "CID": CID
    }

    response = requests.get(url=url, params=params, verify=False)
    res_dict = response.json()

    if res_dict["return"]:
        sizes = res_dict["results"]
        return sizes
    else:
        print(res_dict)
        return None



def list_public_subnets(url=None, CID=None, account_name=None, cloud_type=None, region=None, vpc_id=None):
    """
    This function invokes Aviatrix API "list_public_subnets" and return a list of public subnet information (string)
    """
    public_subnets = list()
    params = {
        "action": "list_public_subnets",
        "CID": CID,
        "account_name": account_name,
        "cloud_type": cloud_type,
        "region": region,
        "vpc_id": vpc_id
    }

    response = requests.get(url=url, params=params, verify=False)
    res_dict = response.json()

    if res_dict["return"]:
        public_subnets = res_dict["results"]
        return public_subnets
    else:
        print(res_dict)
        return None



def create_transit_gw(url=None, CID=None, account_name=None, cloud_type=None, region=None, vpc_id=None,
                      public_subnet=None, gateway_name=None, gateway_size=None, dns_server_ip=None, tags=None):
    data = {
        "action": "create_transit_gw",
        "CID": CID,
        "account_name": account_name,
        "cloud_type": cloud_type,
        "region": region,
        "vpc_id": vpc_id,
        "public_subnet": public_subnet,
        "gw_name": gateway_name,
        "gw_size": gateway_size
    }

    if dns_server_ip is not None:
        data["dns_server"] = dns_server_ip
    if tags is not None:
        data["tags"] = tags

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def enable_transit_ha(url=None, CID=None, gateway_name=None, public_subnet=None, new_zone=None):
    """
    :param new_zone: This field is for GCloud ONLY
    """
    data = {
        "action": "enable_transit_ha",
        "CID": CID,
        "gw_name": gateway_name,
        "public_subnet": public_subnet
    }

    if new_zone is not None:
        data["new_zone"] = new_zone

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def connect_transit_gw_to_vgw(url=None, CID=None, connection_name=None,
                              transit_vpc_id=None, transit_gateway_name=None, bgp_local_as_number=None,
                              vgw_account_name=None, vgw_region=None, vgw_id=None):
    data = {
        "action": "connect_transit_gw_to_vgw",
        "CID": CID,
        "connection_name": connection_name,
        "vpc_id": transit_vpc_id,
        "transit_gw": transit_gateway_name,
        "bgp_local_as_number": bgp_local_as_number,
        "bgp_vgw_account_name": vgw_account_name,
        "bgp_vgw_region": vgw_region,
        "vgw_id": vgw_id
    }

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def create_spoke_gw(url=None, CID=None, account_name=None, cloud_type=None, region=None, vpc_id=None,
                    public_subnet=None, gateway_name=None, gateway_size=None, dns_server_ip=None, tags=None):
    data = {
        "action": "create_spoke_gw",
        "CID": CID,
        "account_name": account_name,
        "cloud_type": cloud_type,
        "region": region,
        "vpc_id": vpc_id,
        "public_subnet": public_subnet,
        "gw_name": gateway_name,
        "gw_size": gateway_size
    }

    if dns_server_ip is not None:
        data["dns_server"] = dns_server_ip
    if tags is not None:
        data["tags"] = tags

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def enable_spoke_ha(url=None, CID=None, gateway_name=None, public_subnet=None, new_zone=None):
    """
    :param new_zone: This field is for GCloud ONLY
    """
    data = {
        "action": "enable_spoke_ha",
        "CID": CID,
        "gw_name": gateway_name,
        "public_subnet": public_subnet
    }

    if new_zone is not None:
        data["new_zone"] = new_zone

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def attach_spoke_to_transit_gw(url=None, CID=None, spoke_gateway=None, transit_gateway=None):
    data = {
        "action": "attach_spoke_to_transit_gw",
        "CID": CID,
        "spoke_gw": spoke_gateway,
        "transit_gw": transit_gateway
    }

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def detach_spoke_from_transit_gw(url=None, CID=None, spoke_gateway_name=None):
    data = {
        "action": "detach_spoke_from_transit_gw",
        "CID": CID,
        "spoke_gw": spoke_gateway_name
    }

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def disconnect_transit_gw_from_vgw(url=None, CID=None, connection_name=None, transit_vpc_id=None):
    data = {
        "action": "disconnect_transit_gw_from_vgw",
        "CID": CID,
        "connection_name": connection_name,
        "vpc_id": transit_vpc_id
    }

    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def delete_gateway(url=None, CID=None, cloud_type=None, gateway_name=None):
    data = {
        "action": "delete_container",
        "CID": CID,
        "cloud_type": cloud_type,
        "gw_name": gateway_name
    }
    response = requests.post(url=url, data=data, verify=False)
    res_dict = response.json()

    return res_dict



def print_farewell_msg():
    print("\nThank you for using Aviatrix!")
    print("Aviatrix  --> Encrypted Tunnel  --> ∧v!@+r!x")
    print("✈ ☁ ✈ Aviatrix ✈ ☁ ✈ The Best Cloud Network Architect!! ✈ ☁ ✈ Aviatrix ✈ ☁ ✈")
    return
