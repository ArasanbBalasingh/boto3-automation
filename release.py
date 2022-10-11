import boto3
import time
import json

# Check for if VPC already exists
def check_VPC_resource(tag, TAG_VALUES):
    try:
        check_vpc_resource = boto3.client("ec2", "ap-south-1")
        paginator = check_vpc_resource.get_paginator('describe_vpcs')
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': TAG_VALUES
                }],
            PaginationConfig={'MaxItems': 10})
        full_result = response_iterator.build_full_result()

        vpc_list = []

        for page in full_result['Vpcs']:
            vpc_list.append(page)
        for i in vpc_list:
            for j in i['Tags']:
                if j['Value'] == TAG_VALUES[0]:
                    return i['VpcId']
        return vpc_list

    except Exception as e:
        print(e)

# VPC Creation
def create_VPC():
    try:
        TAG_VALUES = ['QUBE-VPC']
        TAG = 'Name'
        if check_VPC_resource(TAG, TAG_VALUES):
            print('Existing VPC Detected')
            vpc_id = check_VPC_resource(TAG, TAG_VALUES)
            return vpc_id
        else:
            vpc_resource = boto3.resource("ec2", "ap-south-1")
            vpc_response = vpc_resource.create_vpc(
            CidrBlock = '192.168.0.0/16',
            InstanceTenancy='default',
            TagSpecifications=[{
                'ResourceType': 'vpc',
                'Tags': [{
                    'Key': 'Name',
                    'Value': 'QUBE-VPC'
                    }]
                }])
            return vpc_response.id

    except Exception as e:
        print(e)


# Check If Subnet Already Created
def check_subnet(tag, tag_values):
    try:
        subnetCheck_client = boto3.client("ec2", 'ap-south-1')
        paginator = subnetCheck_client.get_paginator('describe_subnets')
        response_iterator = paginator.paginate(

                Filters=[{
                    'Name': f'tag:{tag}',
                    'Values': tag_values
                    }],
                PaginationConfig = {
                    'MaxItems': 10
                    }
                )
        full_result = response_iterator.build_full_result()
        subnet_list = []
        for page in full_result['Subnets']:
            subnet_list.append(page)
        for i in subnet_list:
            for j in i['Tags']:
                if j['Value'] == tag_values[0]:
                    return i['SubnetId']

        return subnet_list

    except Exception as e:
        print(e)

#Function call to assign PublicIPV4 address
def modify_subnet_attribute(sub_id, map_public_ip_on_launch):
    try:
        vpc_client = boto3.client("ec2", 'ap-south-1')
        print('Trying to assig pub IP')
        response = vpc_client.modify_subnet_attribute(
                MapPublicIpOnLaunch={'Value': map_public_ip_on_launch},
                SubnetId=sub_id
                )
        print('Public IP assigned')
    except Exception as e:
        print(e)

# Function call to create second subnet
def create_second_subnet(vpc_id):
    try:

        TAG_VALUES = ['QUBE-subnet-2']
        TAG = 'Name'
        sub_id = check_subnet(TAG, TAG_VALUES)

        if check_subnet(TAG, TAG_VALUES):
            print('Existing Secondary Subnet Detected')
            return sub_id
        else:
            subnet_resource = boto3.resource("ec2", 'ap-south-1')
            subnet_response = subnet_resource.create_subnet(
                TagSpecifications=[{
                    'ResourceType' : 'subnet',
                    'Tags': [{
                        'Key': 'Name',
                        'Value': 'QUBE-subnet-2'
                        }]},],
            AvailabilityZone='ap-south-1c',
            VpcId=vpc_id,
            CidrBlock='192.168.16.0/20'
                        )
            print('Secondary Subnet Created ')
            # function Call to assign IPV4 Address
            MAP_PUBLIC_IP_ON_LAUNCH = True
            sub_id = subnet_response.id
            map_public_ip_on_launch = True
            modify_subnet_attribute(sub_id, map_public_ip_on_launch)
            return subnet_response.id
    
    except Exception as e:
        print(e)

def create_subnet(vpc_id):

    try:
        TAG_VALUES = ['QUBE-subnet']
        TAG = 'Name'
        sub_id = check_subnet(TAG, TAG_VALUES)
        if check_subnet(TAG, TAG_VALUES):
            print('Existing Subnet Detected')
            return sub_id
        else:
            subnet_resource = boto3.resource("ec2", 'ap-south-1')
            subnet_response = subnet_resource.create_subnet(
                    TagSpecifications=[{
                        'ResourceType' : 'subnet',
                        'Tags': [{
                            'Key': 'Name',
                            'Value': 'QUBE-subnet'
                            }]},
                        ],
            AvailabilityZone='ap-south-1a',
            VpcId=vpc_id,
            CidrBlock='192.168.1.0/20'
                        )
            # function Call to assign IPV4 Address
            MAP_PUBLIC_IP_ON_LAUNCH = True
            sub_id = subnet_response.id
            map_public_ip_on_launch = True
            modify_subnet_attribute(sub_id, map_public_ip_on_launch)
            return subnet_response.id
    except Exception as e:
        print(e)



# Check if IGW already provisioned
def check_IGW(tag, tag_values):
    try:
        check_igw_client = boto3.client("ec2", "ap-south-1")
        paginator = check_igw_client.get_paginator('describe_internet_gateways')

        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],
            PaginationConfig={'MaxItems': 10})

        full_result = response_iterator.build_full_result()

        internet_gateways_list = []

        for page in full_result['InternetGateways']:
            internet_gateways_list.append(page)
        for i in internet_gateways_list:
            for j in i['Tags']:
                if j['Value'] == tag_values[0]:
                    return i['InternetGatewayId']


    except Exception as e:
        print(e)

# Internet Gateway Creation
def create_IGW():
    try:
        TAG_VALUES = ['QUBE-IGW']
        TAG = 'Name'
        igw_value = check_IGW(TAG, TAG_VALUES)

        if check_IGW(TAG, TAG_VALUES):

            igw_value = check_IGW(TAG, TAG_VALUES)
            print('Detected Existing InternetGateWay')
            return igw_value

        else:
            igw_client = boto3.client("ec2", "ap-south-1")
            igw_response = igw_client.create_internet_gateway(
                    TagSpecifications=[{

                        'ResourceType': 'internet-gateway',
                        'Tags': [

                            {
                                'Key': 'Name',
                               'Value': 'QUBE-IGW'
                               },]},]
                            )
            print('InternetGateWay Created')
            return igw_response['InternetGateway']['InternetGatewayId']
    except Exception as e:
        print(e)

# Check if IGW and VPC are already integrated
def check_attach_igw_vpc(tag, tag_values):
    try:
        check_igw_client = boto3.client("ec2", "ap-south-1")
        paginator = check_igw_client.get_paginator('describe_internet_gateways')

        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],
            PaginationConfig={'MaxItems': 10})

        full_result = response_iterator.build_full_result()

        internet_gateways_list = []

        for page in full_result['InternetGateways']:

            internet_gateways_list.append(page)

        for i in internet_gateways_list:
            for j in i['Attachments']:
                if j['State'] == 'available':
                    print('IGW and VPC are already attached ')
                    return True


    except Exception as e:
        print(e)

# Attaching IGW with VPC
def attach_igw_vpc(igw_id, vpc_id):
    try:
        TAG_VALUES = ['QUBE-IGW']
        TAG = 'Name'
        if check_attach_igw_vpc(TAG, TAG_VALUES):
            print('Since the IGW and VPC are integrated already, Skipping this step ')
        else:
            attach_igw_client = boto3.client("ec2", 'ap-south-1')
            attachIGW_response = attach_igw_client.attach_internet_gateway(
                    InternetGatewayId=igw_id,
                    VpcId=vpc_id
                    )
            print('IGW Attached with VPC')
    except Exception as e:
        print(e)


#check if there is already a routing table
def check_routeTable(tag, tag_values):
    try:
        check_RT_client = boto3.client("ec2", 'ap-south-1')
        paginator = check_RT_client.get_paginator('describe_route_tables')
        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],
            PaginationConfig={'MaxItems': 10})

        full_result = response_iterator.build_full_result()

        route_tables_list = []

        for page in full_result['RouteTables']:
            route_tables_list.append(page)
        for i in route_tables_list:
            for j in i['Tags']:
                if j['Value'] == tag_values[0]:
                    return i['RouteTableId']
    except Exception as e:
        print(e)


# Creating Routing Table
def create_routingTable(vpc_id):
    try:
        TAG_VALUES = ['QUBE-RT']
        TAG = 'Name'
        resultList = check_routeTable(TAG, TAG_VALUES)
        if check_routeTable(TAG, TAG_VALUES):
            print('Existing Route table detected')
            return resultList
        else:
            routeTable_client = boto3.client("ec2", 'ap-south-1')
            routeTable_response = routeTable_client.create_route_table(
                VpcId=vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'QUBE-RT'
                                },]},])
            print('New RouteTabel created')
            for i in routeTable_response['RouteTable']['Tags']:
                if i['Value'] == TAG_VALUES[0]:
                    return routeTable_response['RouteTable']['RouteTableId']
    except Exception as e:
        print(e)

# Creating Routes
def create_Routes(destination_cidr_block, gateway_id, route_table_id):
    try:
        route_client = boto3.client("ec2", 'ap-south-1')
        response = route_client.create_route(
            DestinationCidrBlock=destination_cidr_block,
            GatewayId=gateway_id,
            RouteTableId=route_table_id)
        print('Route Creation Successfull')
    except Exception as e:
        print(e)


# Associating RouteTable with Subnet
def associate_RT(route_table_id, subnet_id):
    try:
        associate_client = boto3.client("ec2", 'ap-south-1')
        response = associate_client.associate_route_table(

            RouteTableId=route_table_id,
            SubnetId=subnet_id
            )
        print('RouteTable Association with Subnet Successfull')

    except Exception as e:
        print(e)

#Check if any existing KeyPair
def check_keyPair(keyname):
    try:  
        client = boto3.client('ec2')
        response = client.describe_key_pairs(
            KeyNames=[
                keyname,
            ],
        )

        for i in response['KeyPairs']:
            if i['KeyName'] == keyname:
                return True
    
    except Exception as e:
        return False

# Create Key-pair
def createKeyPair(keyname):

    try:
        print(' ********************** Running tests to detect  if Key Pair Already Exists with the name : ' + keyname )
        keyPairID = check_keyPair(keyname)
        if check_keyPair(keyname):
            print('Key-Pair already exists in the name : ' +keyname+ ', proceeding next step')
            return keyPairID
        else:
            print('No Matching Key-pair found, hence creating one')
            client = boto3.client('ec2')
            response = client.create_key_pair(
            KeyName = keyname,
            )
    
            return response['KeyName']

    except Exception as e:
        print(e)


#Describe Security groups
def describe_security_groups_rules(security_group_ids, max_items):
    try:
        sec_list = [security_group_ids]
        vpc_client = boto3.client("ec2", 'ap-south-1')
        paginator = vpc_client.get_paginator('describe_security_group_rules')

        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': 'group-id',
                'Values': sec_list
            }],
            PaginationConfig={'MaxItems': max_items})

        full_result = response_iterator.build_full_result()

        security_groups_rules = []

        for page in full_result['SecurityGroupRules']:
            security_groups_rules.append(page)
        var_id = security_group_ids
        for i in security_groups_rules:
            if i['GroupId'] == var_id:
                if i['IpProtocol'] == 'tcp'and i['FromPort']:
                    print('Existing Protocol and Routes Configuration been Detected with this security group')
                    return True

        print(security_groups_rules)
    except Exception as e:
        print(e)


# Check security group name
def check_security_group(tag, tag_values):
    try:
        vpc_client = boto3.client("ec2", 'ap-south-1')
        paginator = vpc_client.get_paginator('describe_security_groups')

        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            Filters=[{
                'Name': f'tag:{tag}',
                'Values': tag_values
            }],

            PaginationConfig={'MaxItems': 10})

        full_result = response_iterator.build_full_result()

        security_groups_list = []

        for page in full_result['SecurityGroups']:
            security_groups_list.append(page)
        for i in security_groups_list:
            if i['GroupName'] == tag_values[0]:
                return i['GroupId']
    except Exception as e:
        print(e)

#Security Group Creation
def create_security_group(group_name, vpc_id, description):
    try:
        tag = 'Name'
        tag_values = [group_name]
        if check_security_group(tag, tag_values):
            print('Existing Security Group Detected')
            sec_id = check_security_group(tag, tag_values)
            return sec_id
        else: 
            print('Creating a New Security Group for VPC ' + vpc_id)
            client = boto3.client('ec2')
            response = client.create_security_group(
                Description=description,
                GroupName=group_name,
                VpcId=vpc_id,
                TagSpecifications=[{
                    'ResourceType':'security-group',
                    'Tags': [{
                        'Key':'Name',
                        'Value': group_name
                        }]}])
            return response['GroupId']
    except Exception as e:
        print(e)

# Creating inbound request acceptance
def add_inbound_rule_to_sg(security_group_id):
    try:
        #describe_security_groups_rules(security_group_id, 10)
        if describe_security_groups_rules(security_group_id, 10):
            print('The inbound rules were already registered with the security group')

        else:
            print('Adding inbound public access to Security Group ' + security_group_id)
            vpc_client = boto3.client("ec2", 'ap-south-1')
            response = vpc_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        },
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 22,
                            'ToPort': 22,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                            }
                            ])
            print('Inbound rule were added successfully')

    except Exception as e:
        print(e)


# EC2-Instance Provisioning
def create_ec2_instance(sub_id, keyPairName, security_group_id):
    try:
        print("******************** Running Tests to Check If EC2 is already provisioned **********************")
        ec2ID = check_ec2_resource()
        if check_ec2_resource():
            print('********** EC2 Instance found existing, Proceeding to next step for ELB creation **********')
            return ec2ID
        else:
            print("********** EC2 Not found, hence Provisioning EC2 Instance **********")
            resource_ec2 = boto3.client("ec2")
            resource_ec2_response = resource_ec2.run_instances(
                ImageId = "ami-064687fa05edcd686",
                MinCount = 1,
                MaxCount = 1,
                InstanceType="t2.micro",
                SecurityGroupIds=[security_group_id],
                SubnetId= sub_id,
                KeyName = keyPairName,
                UserData="""#!/bin/bash
                    yum update -y
                    yum install httpd -y
                    service httpd start
                    echo "<html><body><h1>Hello World.</h1></body></html>" > /var/www/html/index.html"""
                    )
            print('Configuration of EC2, Installation of Apache WebServers are in progress')
            waiter = resource_ec2.get_waiter('instance_status_ok')
            waiter.wait(
                    InstanceIds=[resource_ec2_response['Instances'][0]['InstanceId']],

                    )
            print("********** EC2 Provisioned Successfully, Creation of TAG begins and successfull **********")
            tagCreation_EC2(resource_ec2_response['Instances'][0]['InstanceId'])
            return resource_ec2_response['Instances'][0]['InstanceId']

    except Exception as e:
            print(e)

# CREATE TAG FOR EC2
def tagCreation_EC2(EC2_Instance_ID):
    client = boto3.client('ec2')
    response = client.create_tags(
        Resources=[
            EC2_Instance_ID,
            ],
        Tags=[
            {
            'Key': 'Name',
            'Value': 'QUBETEST'
        },
    ]
)

# DESCRIBE THE INSTANCE AND CHECK FOR TAG VALUES IF EXIST ALREADY
def check_ec2_resource():
    ec2ID = ''
    client = boto3.client('ec2')
    myinstance = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': ['QUBETEST']}])
    resp = myinstance['Reservations']
    if resp:
        ec2ID = resp[0]['Instances'][0]['InstanceId']
        return ec2ID

    else:
        print('No EC2 found, provisioning kicked off')
        return False


# ELB Check if it is already existing
def check_elb_resource(lbname):
    lbName = []
    lbcList = []
    elb_client = boto3.client('elbv2')
    LoadBalance = elb_client.describe_load_balancers()
    for lb in LoadBalance['LoadBalancers']:
        lbName.append(lb["LoadBalancerName"])
    if "TESTLoadBalancer" in lbName:
        for lbc in LoadBalance['LoadBalancers']:
            if lbc["LoadBalancerName"] == lbname:
                lbcList.append(lbc['LoadBalancerArn'])
                lbcList.append(lbc['DNSName'])
                return lbcList
    else:
        return False

# Elastic Load Balancer Creation
def create_elb(sub_id, sub_id_sec, sec_g_id, lbName):
    try:
        LB_List = []
        print("Checking if LoadBalancer Already Exists")
        NewList = check_elb_resource(lbName)
        if check_elb_resource(lbName):
            print("LoadBalancer Available, Hence proceeding for TargetGroup Creation")
            elb_client = boto3.client('elbv2')
            LoadBalance = elb_client.describe_load_balancers()
            return NewList
        else:
            print("No LoadBalancer found, Hence Creating Application Load Balancer")
            elb_client = boto3.client('elbv2')
            elb_response = elb_client.create_load_balancer(
                Name = lbName,
                Subnets = [
                    sub_id,
                    sub_id_sec,
                    ],
                SecurityGroups=[
                    sec_g_id,
                ],
                Type='application'
            )
            print('Application Load Balancer Creation is in-progress')
            for i in elb_response['LoadBalancers']:
                LB_List.append(i['LoadBalancerArn'])
                LB_List.append(i['DNSName'])
                return LB_List

    except Exception as e:
        print(e)


# Check if Target Group is already available
def check_TG_resource(tgName):
    tg_Name = []
    target_ARN = ''
    elb_client = boto3.client('elbv2')
    TG_check = elb_client.describe_target_groups()
    for TG in TG_check['TargetGroups']:
        tg_Name.append(TG['TargetGroupName'])
    if 'TEST-target-group' in tg_Name:
        for tgl in TG_check['TargetGroups']:
            if tgl['TargetGroupName'] == tgName:
                target_ARN = tgl['TargetGroupArn']
                return target_ARN
    else:
        return False


# Target Group Creation
def create_targetGroup(vpc_id, tgName):
    try:
        target_ARN = check_TG_resource(tgName)
        if check_TG_resource(tgName):
            print("Target Group already exists, proceeding for ELB-Listeners Creation")
            return target_ARN
        else:
            print("Creating Target Group")
            elb_client = boto3.client('elbv2')
            elb_targetGroup_response = elb_client.create_target_group(
                Name = tgName,
                Protocol = 'HTTP',
                Port = 80,
                VpcId = vpc_id,
                ProtocolVersion = 'HTTP1',
                TargetType = 'instance',
                )
            for i in elb_targetGroup_response['TargetGroups']:
                return i['TargetGroupArn']

    except Exception as e:
        print(e)


# Check if we have listeners already configured
def check_Listener_resource(LB_arn_value, TG_ARN):
    l_Name = []
    elb_client = boto3.client('elbv2')
    Listener_check = elb_client.describe_listeners(
            LoadBalancerArn = LB_arn_value

            )
    for lc in Listener_check['Listeners']:
        for ld in lc['DefaultActions']:
            if ld['TargetGroupArn'] == TG_ARN:
                return True
            else:
                return False

# Listeners Creation for Load Balancer
def create_listener_elb(LB_arn_value, TG_ARN):
    try:

        if check_Listener_resource(LB_arn_value, TG_ARN):
            print("Looks like already listening to the target group")
        else:
            print('No Listeners found for the LoadBalancer specified, configuring now....')
            LoadBalancerArn = LB_arn_value
            elb_client = boto3.client('elbv2')
            elb_listeners_response = elb_client.create_listener(
            LoadBalancerArn= LB_arn_value,
            Protocol = 'HTTP',
            Port = 80,
            DefaultActions=[{
                'Type' : 'forward',
                'TargetGroupArn' : TG_ARN,
                }]
                )
            return elb_listeners_response

    except Exception as e:
        print(e)


#def check registered resource
def check_registeredTarget_resource(TG_ARN, EC2_Instance_ID):
    l_Name = []
    elb_client = boto3.client('elbv2')
    registeredtarget_check = elb_client.describe_target_health(
            TargetGroupArn = TG_ARN,
            Targets=[
                {
                    'Id' : EC2_Instance_ID,
                }
            ]
            )
    for lc in registeredtarget_check['TargetHealthDescriptions']:
        if lc['Target']['Id'] == EC2_Instance_ID and lc['TargetHealth']['State'] == 'healthy':
            return True
        else:
            return False



# Registering Targets with EC2
def register_ec2_targets(TG_arn_value, EC2_Instance_ID):
    try:
        tgValue = TG_arn_value
        EC2value = EC2_Instance_ID
        if check_registeredTarget_resource(tgValue, EC2value):
            print('The instance that you are trying to register is already registered, Dont worry!!')
        else:
            elb_client = boto3.client('elbv2')

            print('Target Registration is in progress')
            elb_registerTarget_response = elb_client.register_targets(
            TargetGroupArn= TG_arn_value,
            Targets=[
                {
              'Id': EC2_Instance_ID,
              }])
            print('Target registered success')
            return elb_registerTarget_response

    except Exception as e:
        print(e)

#check for existing api gateways
def check_apiGateway_resource(apiName):
    try:
        gateList = []
        apiGateway_client = boto3.client('apigatewayv2')
        apiGateway_client_response = apiGateway_client.get_apis()
        for z in apiGateway_client_response['Items']:
            for m in range(len(apiGateway_client_response['Items'])):
                gateList.append(apiGateway_client_response['Items'][m]['Name'])
                if apiGateway_client_response['Items'][m]['Name'] == apiName:
                    apiid = apiGateway_client_response['Items'][m]['ApiId']
                    return apiid

    except Exception as e:
        print(e)

# Creating API Gateway
def create_api_gateway(apiName):
    try:
        response = check_apiGateway_resource(apiName)
        if check_apiGateway_resource(apiName):
            print('Api Gateway already present')
            return response
        else:
            apiGateway_client = boto3.client('apigatewayv2')
            apiGateway_response = apiGateway_client.create_api(
                    Name= apiName,
                    ProtocolType = 'HTTP'
            )
            print('API Gateway created')
            return apiGateway_response['ApiId']

    except Exception as e:
        print(e)
#Check if there is a route configured already for you API gateway

def check_route(api_id_value):
    try:
        apiRouteCheck_client = boto3.client('apigatewayv2')
        apiRouteCheck_response = apiRouteCheck_client.get_routes(
                ApiId = api_id_value
                )
        for i in range(len(apiRouteCheck_response['Items'])):
            if apiRouteCheck_response['Items'][i]['RouteKey'] == 'ANY /{proxy+}':
                return True

    except Exception as e:
        print(e)

# Establishing Route for API Gateway
def create_route(api_id_value, integrationID):
    try:
        if check_route(api_id_value):
            print('Route  configuration already exists for this API')
        else:
            apiGatewayRoute_client = boto3.client('apigatewayv2')
            apiGatewayRoute_response = apiGatewayRoute_client.create_route(
            ApiId = api_id_value,
            RouteKey = 'ANY /{proxy+}',
            Target = 'integrations/'+integrationID
            )
            print('Route Created')
            return apiGatewayRoute_response

    except Exception as e:
        print(e)


# Integration Rule for API GateWay
def create_integration_gateway(api_id_value, DNS_Value):
    try:
        apiGatewayIntegration_client = boto3.client('apigatewayv2')
        apiGatewayIntegration_response = apiGatewayIntegration_client.create_integration(
            ApiId = api_id_value,
            IntegrationType = 'HTTP_PROXY',
            IntegrationMethod = 'ANY',
            IntegrationUri = 'http://' + DNS_Value,
            PayloadFormatVersion = '1.0'
            )
        print('Integration Rule Created')
        return apiGatewayIntegration_response

    except Exception as e:
        print(e)


#Checking if there is a Stage Config already

def check_stage(api_id_value):

    try:
        apiStageCheck_client = boto3.client('apigatewayv2')
        apiStageCheck_response = apiStageCheck_client.get_stages(
                ApiId = api_id_value
                )
        for i in range(len(apiStageCheck_response['Items'])):
            if apiStageCheck_response['Items'][i]['StageName'] == '$default':
                status = True
                return status

    except Exception as e:
        print(e)


# Create Stage for API Gateway
def create_stage_gateway(api_id_value):
    try:
        if check_stage(api_id_value):
            print('Stage already Available')
        else:
            apiGatewayStage_client = boto3.client('apigatewayv2')
            apiGatewayStage_response = apiGatewayStage_client.create_stage(
            ApiId = api_id_value,
            AutoDeploy = True,
            StageName = '$default'
            )
            print("Stage Created for API Gateway")
            return apiGatewayStage_response

    except Exception as e:
        print(e)


# Describe IAM role
def check_iam_role(rolename):
    try:
        IAM_RESOURCE = boto3.resource('iam')
        roles = IAM_RESOURCE.roles.all()
        thisList = []
        for role in roles:
            thisList.append(role.role_name)
        if rolename in thisList:
            return True
        else:
            return False

    except Exception as e:
        print(e)


# IAM Role Creation
def create_iam_role(rolename):

    try:
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": 
                    {
                        "Service": "ec2.amazonaws.com",
                        },
                        "Action": "sts:AssumeRole",
        },
    ],
}    
        if check_iam_role(rolename):
            print('IAM role has been already created with this name try different name')
        else:
            client = boto3.client('iam')
            response = client.create_role(
                    RoleName = rolename,
                    AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                    )
    except Exception as e:
        print(e)


# Attaching policy to the created role
def attach_policy():
    try:
        ROLE_NAME = 'test-role'
        resource = boto3.resource('iam')
        role = resource.Role(ROLE_NAME)
        role.attach_policy(
        PolicyArn='arn:aws:iam::aws:policy/AmazonEC2FullAccess' )
        print('Policy has been attached to the IAM role')
    except Exception as e:
        print(e)


# List and Check Instance Profile
def check_instance_profile(instanceProName):
    try:
        IAM_RESOURCE = boto3.resource('iam')
        instance_profiles = IAM_RESOURCE.instance_profiles.all()
        instanceList = []
        for instance_profile in instance_profiles:
            instanceList.append(instance_profile.name)

        if instanceProName in instanceList:
            return True
        else:
            return False
    except Exception as e:
        print(e)
# Instance profile creation
def create_instance_profile(instanceProName):
    try:
        if check_instance_profile(instanceProName):
            print('Instance profile already exisits for the requested name')
        else:
            client = boto3.client('iam')
            response = client.create_instance_profile(
                    InstanceProfileName=instanceProName
                    )
            print('Instance profile created')

    except Exception as e:
        print(e)

# Check for InstanceSessions
def check_instanceSessions(instanceProName, rolename):
    try:
        client = boto3.client('iam')
        response = client.get_instance_profile(
                InstanceProfileName=instanceProName
                )
        for i in response['InstanceProfile']['Roles']:
            if i['RoleName'] == rolename:
                return True
            else:
                return False

    except Exception as e:
        print(e)


# Adding role to IAM instance profile
def addRole_to_InstanceProfile(instanceProName, rolename):
    try:
        if check_instanceSessions(instanceProName, rolename):
            print(' Already role added to this instance profile')
        else:
            IAM_RESOURCE = boto3.resource('iam')
            instance_profile = IAM_RESOURCE.InstanceProfile(instanceProName)
            instance_profile.add_role(RoleName=rolename)
            print('IAM role has been added to the Instance Profile')
    except Exception as e:
        print(e)

# Gathering instance profile
def get_instance_profile(instance_profile_name):
    try:
        iam_client = boto3.client('iam')
        response = iam_client.get_instance_profile(
            InstanceProfileName=instance_profile_name
            )
        return response['InstanceProfile']
    except Exception as e:
        print(e)


# Attaching Role with Instance profile
def associate_iam_instance_profile(instance_profile, EC2_Instance_ID):

    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.associate_iam_instance_profile(
        IamInstanceProfile={
            'Arn': instance_profile['Arn'],
            'Name': instance_profile['InstanceProfileName']
            },
            InstanceId= EC2_Instance_ID
            )
        return response
    
    except Exception as e:
        return False

def main():

    # VPC Creation
    vpc_id = create_VPC()

    # Subnet Creation
    sub_id = create_subnet(vpc_id)
    
    # Function call to create secondary subnet
    sub_id_sec = create_second_subnet(vpc_id)

    # InternetGateway Creation
    igw_id = create_IGW()

    # IGW attachment to VPC
    attach_igw_vpc(igw_id, vpc_id)

    # Route Table Creation
    RT_id = create_routingTable(vpc_id)

    # Route Creation
    destination_cidr_block = '0.0.0.0/0'
    create_Routes(destination_cidr_block, igw_id, RT_id)

    # Routes Association
    associate_RT(RT_id, sub_id)

    # Security Group Creation
    group_name = 'New-Security'
    description = 'Security Group for EC2 and ALB'
    sec_g_id = create_security_group(group_name, vpc_id, description)
    
    # Adding Inbound Rules
    add_inbound_rule_to_sg(sec_g_id)

    # Key-Pair creation
    keyname = 'QUBE-Key'
    keyPairName = createKeyPair(keyname)

    # EC2 Server Provisioning
    EC2_Instance_ID = create_ec2_instance(sub_id, keyPairName, sec_g_id)

    # IAM role creation
    rolename = 'test-role'
    create_iam_role(rolename)

    # Attaching IAM policy for the created role
    attach_policy()

    # Instance profile creation
    instanceProName = 'TestInstanceProfile'
    create_instance_profile(instanceProName)

    # Add role to profile
    addRole_to_InstanceProfile(instanceProName, rolename)
    
    # Gathering Details
    instance_profile = get_instance_profile('TestInstanceProfile')

    # Associating a role to EC2
    if associate_iam_instance_profile(instance_profile, EC2_Instance_ID):
        print('Association successfull')
    else:
        print('Already associated')

    # Application LoadBalancer Provisioning
    lbName = 'QUBE-LB'
    LB = create_elb(sub_id, sub_id_sec, sec_g_id, lbName)
    client = boto3.client('elbv2')
    waiter = client.get_waiter('load_balancer_available')
    waiter.wait(LoadBalancerArns=[LB[0]],)
    print('Application LoadBalancer is created and in Available stat')

    # TargetGroup Creation
    tgName = 'QUBE-TARGET'
    TG_ARN = create_targetGroup(vpc_id, tgName)
    LB_arn_value = LB[0]
    DNS_Value = LB[1]


    # Listener Creation For LoadBalancer
    create_listener_elb(LB_arn_value, TG_ARN)

    # Registering Target Instance with LoadBalancer
    register_ec2_targets(TG_ARN, EC2_Instance_ID)
    client = boto3.client('elbv2')
    waiter = client.get_waiter('target_in_service')
    waiter.wait(TargetGroupArn=TG_ARN,
            Targets=[{
                'Id' : EC2_Instance_ID
                },],
            )

    # API Gateway Provisioning
    apiName = 'QUBE-GATEWAY'
    api_id_value = create_api_gateway(apiName)

    # Integration Rule Creation
    var1 = create_integration_gateway(api_id_value, DNS_Value)
    integrationID = var1['IntegrationId']

    # Route Creation for API-Gateway
    create_route(api_id_value, integrationID)

    # Stage Creation
    create_stage_gateway(api_id_value)
    
    print('\n')
    print('**************  SCRIPT RUN SUCCESSFULL  **********************')
    print('\n')
    print('Kindly access the API GateWay URL : ''https://'+api_id_value+'.execute-api.ap-south-1.amazonaws.com')
    print('\n')
    print('Note: This might take upto 30s to up and running')
    print('\n')

if __name__ == "__main__":
    main()
