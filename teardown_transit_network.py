#!/usr/bin/python3
#-*- coding: UTF-8 -*-


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
        print_farewell_msg()



        ### A: Read Configuration File
        print("\nSTART: Reading script configuration file...")
        config = read_config_file(path_to_config_file)



        ### B: Get script-control-configurations
        pause_on_every_step = config["script_config"]["pause_on_every_step"]
        display_results = config["script_config"]["display_results"]

        print("\nScript Configurations are shown below: ")
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



        ##### START: Tearing-Down Transit Network #####



        if pause_on_every_step == "yes":
            print("Enter anything to start the Teardown process: ")
            os.system("pause")

        print("\n\nTeardown starting in ...")
        for i in range(5, 0, -1):
            time.sleep(1)
            print(i)



        ### E: Get all the Spoke Gateways into a list
        spoke_gws = config["spoke_gateways"]
        vgw_and_tgw_connection_name = config["vgw"]["connection_name"]
        tgw_cloud_type = config["transit_gateway"]["cloud_type"]
        tgw_vpc_id = config["transit_gateway"]["vpc_id"]
        tgw_name = config["transit_gateway"]["gateway_name"]

        ##### Iterate the spoke_gws list to ...
        #         1) Detach Spoke Gateway from Transit Gateway
        #         2) Delete Spoke Peer HA Gateway
        #         3) Delete Spoke Gateway

        for i in range(len(spoke_gws)):

            ### for 1) Detach Spoke Gateway from Transit Gateway
            print("\nSTART: Detach Spoke Gateway from Transit Gateway")

            if pause_on_every_step == "yes":
                os.system("pause")

            spoke_gw_name = spoke_gws[i]["gateway_name"]
            res_dict = detach_spoke_from_transit_gw(url=url,
                                                    CID=CID,
                                                    spoke_gateway_name=spoke_gw_name)
            if display_results == "yes":
                print(res_dict)



            ### for 2) Delete Spoke Peer HA Gateway
            print("\nSTART: Delete Spoke Peer HA Gateway")

            if pause_on_every_step == "yes":
                os.system("pause")

            cloud_type = config["spoke_gateways"][i]["cloud_type"]
            spoke_gw_hagw_name = spoke_gw_name + "-hagw"
            res_dict = delete_gateway(url=url, CID=CID, cloud_type=cloud_type, gateway_name=spoke_gw_hagw_name)

            if display_results == "yes":
                print(res_dict)



            ### for 3) Delete Spoke Gateway
            print("\nSTART: Delete Spoke Gateway")

            if pause_on_every_step == "yes":
                os.system("pause")

            res_dict = delete_gateway(url=url, CID=CID, cloud_type=cloud_type, gateway_name=spoke_gw_name)

            if display_results == "yes":
                print(res_dict)
        # end for



        ### F: Disconnect VGW from Transit Gateway
        print("\nSTART: Disconnect VGW from Transit Gateway")

        if pause_on_every_step == "yes":
            os.system("pause")

        res_dict = disconnect_transit_gw_from_vgw(url=url,
                                                  CID=CID,
                                                  connection_name=vgw_and_tgw_connection_name,
                                                  transit_vpc_id=tgw_vpc_id)
        if display_results == "yes":
            print(res_dict)



        ### G: Delete Transit Peer HA Gateway
        print("\nSTART: Delete Transit Peer HA Gateway")

        if pause_on_every_step == "yes":
            os.system("pause")

        tgw_hagw_name = tgw_name + "-hagw"
        res_dict = delete_gateway(url=url, CID=CID, cloud_type=tgw_cloud_type, gateway_name=tgw_hagw_name)
        if display_results == "yes":
            print(res_dict)



        ### H: Delete Transit Gateway
        print("\nSTART: Delete Transit Gateway")

        if pause_on_every_step == "yes":
            os.system("pause")

        res_dict = delete_gateway(url=url, CID=CID, cloud_type=tgw_cloud_type, gateway_name=tgw_name)
        if display_results == "yes":
            print(res_dict)



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
