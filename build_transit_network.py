#!/usr/bin/python3
#-*- coding: UTF-8 -*-


"""
Objectives:
    This Python project demonstrates using Aviatrix API to build a Transit Network solution.


References:
    1. Aviatrix Official Website
        www.aviatrix.com

    2. Aviatrix Transit Network Documentation
        http://docs.aviatrix.com/HowTos/transitvpc_workflow.html

    3. Contact Aviatrix
        SALES:   sales@aviatrix.com
        SUPPORT: support@aviatrix.com

    4. Aviatrix API Documentation
        https://s3-us-west-2.amazonaws.com/avx-apidoc/index.htm


Prerequisites:
    1. Aviatrix Cloud Controller with version 3.1 or later
    2. Controller Cloud-Account  (Currently it needs to be AWS based)
    3. Aviatrix Customer ID (only if your controller image is "BYOL")
    4. At least 2 VPCs (for Transit and Spoke) and 1 VGW available and not being used


More info:
    * To finish building the topology, it takes roughly 15-30 min (with 2 Spoke Gateways) depending on the region.


Author:
Ryan Liu (Aviatrix Engineering Department)


"""


import os
import traceback
import time
import json
from json.decoder import *
from lib.util import *


if __name__ == "__main__":
    path_to_config_file = "config/config.json"

    try:
        ### Aviatrix Greeting
        print_greeting_msg()



        ### A: Read Configuration File
        print("\nSTART: Reading script configuration file...")
        config = read_config_file(path_to_config_file)



        ### B: Get script-control-configurations
        ha_enabled = config["script_config"]["ha_enabled"]
        pause_on_every_step = config["script_config"]["pause_on_every_step"]
        display_results = config["script_config"]["display_results"]

        print("\nScript Configurations are shown below: ")
        print("    HA Enabled: " + ha_enabled)
        print("    Pause on every STEP: " + pause_on_every_step)
        print("    Display Result on every STEP: " + display_results)



        print("\nScript begins!")



        ### C: Check Requirements
        print("\nSTART: Checking script requirements...")
        if check_requirements(config):
            print("    Successfully passed requirements check!")
        else:
            print("    Failed to pass requirements check")
            print("Error: Please terminate the script and check if all requirements are met...")
            os.system("pause")



        ### D: Login Aviatrix Controller and Get CID
        print("\nSTART: Login Aviatrix Controller, and get CID")

        if pause_on_every_step == "yes":
            os.system("pause")

        controller_ip = config["controller"]["public_ip"]
        admin_password = config["controller"]["admin_password"]
        url = "https://" + controller_ip + "/v1/api"
        CID = login(url=url, username="admin", password=admin_password)

        print("    Successfully logged onto controller! CID: " + CID)



        ##### START: Building Transit Network #####



        ### E: Transit Network Step 01: Launch a Transit VPC GW
        print("\nSTART: Transit Network Step 01: Launch a Transit VPC GW")

        if pause_on_every_step == "yes":
            os.system("pause")

        tgw_account_name = config["controller"]["cloud_account"]
        tgw_cloud_type = config["transit_gateway"]["cloud_type"]
        tgw_region = config["transit_gateway"]["region"]
        tgw_vpc_id = config["transit_gateway"]["vpc_id"]
        tgw_public_subnet = config["transit_gateway"]["public_subnet"]
        tgw_name = config["transit_gateway"]["gateway_name"]
        tgw_size = config["transit_gateway"]["gateway_size"]
        tgw_dns_server_ip = config["transit_gateway"]["dns_server_ip"]
        tgw_tags = config["transit_gateway"]["tags"]

        res_dict = create_transit_gw(url=url,
                                     CID=CID,
                                     account_name=tgw_account_name,
                                     cloud_type=tgw_cloud_type,
                                     region=tgw_region,
                                     vpc_id=tgw_vpc_id,
                                     public_subnet=tgw_public_subnet,
                                     gateway_name=tgw_name,
                                     gateway_size=tgw_size,
                                     dns_server_ip=tgw_dns_server_ip,
                                     tags=tgw_tags)

        if display_results == "yes":
            print(res_dict)



        ### F: Transit Network Step 02: Enable HA at Transit GW
        if ha_enabled == "yes":

            print("\nSTART: Transit Network Step 02: Enable HA at Transit GW")

            if pause_on_every_step == "yes":
                os.system("pause")

            ha_public_subnet = config["transit_gateway"]["ha_configuration"]["ha_public_subnet"]
            res_dict = enable_transit_ha(url=url, CID=CID, gateway_name=tgw_name, public_subnet=ha_public_subnet)

            if display_results == "yes":
                print(res_dict)



        ### G: Transit Network Step 03: Connect to VGW
        print("\nSTART: Transit Network Step 03: Connect to VGW")

        if pause_on_every_step == "yes":
            os.system("pause")

        connection_name = config["vgw"]["connection_name"]
        bgp_local_as_number = config["vgw"]["bgp_local_as_number"]
        cloud_account = config["vgw"]["cloud_account"]
        region = config["vgw"]["region"]
        vpc_id = config["vgw"]["vpc_id"]
        vgw_id = config["vgw"]["vgw_id"]
        res_dict = connect_transit_gw_to_vgw(url=url, CID=CID, connection_name=connection_name,
                                             transit_vpc_id=tgw_vpc_id, transit_gateway_name=tgw_name,
                                             bgp_local_as_number=bgp_local_as_number,
                                             vgw_account_name=tgw_account_name, vgw_region=tgw_region, vgw_id=vgw_id)

        if display_results == "yes":
            print(res_dict)



        ### H: Get all the Spoke Gateways into a list
        spoke_gws = list()
        spoke_gws = config["spoke_gateways"]


        ##### Iterate the spoke_gws list to ...
        #         1) Create Spoke Gateway
        #         2) Enable Peer HA for Spoke Gateway(if HA enabled)
        #         3) Attach Spoke Gateway to Transit Gateway

        for i in range(len(spoke_gws)):
            ### I: for 1) Transit Network Step 04: Create Spoke Gateway
            print("\nSTART: Transit Network Step 04: Launch a Spoke Gateway")

            if pause_on_every_step == "yes":
                os.system("pause")

            cloud_type = spoke_gws[i]["cloud_type"]
            region = spoke_gws[i]["region"]
            vpc_id = spoke_gws[i]["vpc_id"]
            public_subnet = spoke_gws[i]["public_subnet"]
            spoke_gw_name = spoke_gws[i]["gateway_name"]
            gateway_size = spoke_gws[i]["gateway_size"]
            dns_server_ip = spoke_gws[i]["dns_server_ip"]
            nat_enabled = spoke_gws[i]["nat_enabled"]
            tags = spoke_gws[i]["tags"]

            res_dict = create_spoke_gw(url=url,
                                       CID=CID,
                                       account_name=tgw_account_name,
                                       cloud_type=cloud_type,
                                       region=region,
                                       vpc_id=vpc_id,
                                       public_subnet=public_subnet,
                                       gateway_name=spoke_gw_name,
                                       gateway_size=gateway_size,
                                       dns_server_ip=dns_server_ip,
                                       tags=tags)

            if display_results == "yes":
                print(res_dict)



            ### J: for 2) Transit Network Step 05: Enable Spoke HA
            if ha_enabled == "yes":

                print("\nSTART: Transit Network Step 05: Enable Spoke Gateway HA")

                if pause_on_every_step == "yes":
                    os.system("pause")

                ha_public_subnet = spoke_gws[i]["ha_configuration"]["ha_public_subnet"]
                res_dict = enable_spoke_ha(url=url, CID=CID, gateway_name=spoke_gw_name, public_subnet=public_subnet)

                if display_results == "yes":
                    print(res_dict)



            ### K: for 3) Transit Network Step 06: Attach Spoke GW to Transit VPC
            print("\nSTART: Transit Network Step 06: Attach Spoke GW to Transit VPC")

            if pause_on_every_step == "yes":
                os.system("pause")

            ha_public_subnet = spoke_gws[i]["ha_configuration"]["ha_public_subnet"]
            res_dict = attach_spoke_to_transit_gw(url=url,
                                                  CID=CID,
                                                  spoke_gateway=spoke_gw_name,
                                                  transit_gateway=tgw_name)

            if display_results == "yes":
                print(res_dict)
        # end for


        ### END
        print_farewell_msg()


    except FileNotFoundError as err:
        print("\n\n****************************************************************************************  \n")
        print("Oops! Aviatrix Robot Catches an Error/Exception!")
        print("    Please check the PATH to the configuration file.")
        print("Traceback detail is below...\n")
        tracekback_msg = traceback.format_exc()
        print(tracekback_msg)
        print("****************************************************************************************  \n")


    except KeyError as err:
        print("\n\n****************************************************************************************  \n")
        print("Oops! Aviatrix Robot Catches an Error/Exception!")
        print("    Check the 'key' you're looking is in the 'config.json' file.")
        print("Traceback detail is below...\n")
        tracekback_msg = traceback.format_exc()
        print(tracekback_msg)
        print("****************************************************************************************  \n")


    except JSONDecodeError as err:
        print("\n\n****************************************************************************************  \n")
        print("Oops! Aviatrix Robot Catches an Error/Exception!")
        print("    Please check the format of config.json file. Maybe forgot to remove a comma ',' OR end with a double-quote '\"' ")
        print("Traceback detail is below...\n")
        tracekback_msg = traceback.format_exc()
        print(tracekback_msg)
        print("****************************************************************************************  \n")


    except Exception as err:
        print("\n\n****************************************************************************************  \n")
        print("Oops! Aviatrix Robot Catches an Error/Exception!")

        print("Traceback detail is below...\n")
        tracekback_msg = traceback.format_exc()
        print(tracekback_msg)
        print("****************************************************************************************  \n")


    finally:
        pass

##### END if __name__ == "__main__":
