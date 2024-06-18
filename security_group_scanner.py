import aws_utils
import menu_builder
import utils


class AuthInfo:
    def __init__(self, auth_type=None, key=None, secret=None, profile_name=None, role_arn=None):
        self.AuthType = auth_type
        self.Key = key
        self.Secret = secret
        self.ProfileName = profile_name
        self.RoleArn = role_arn


class SecurityGroup:
    def __init__(self):
        self.description = None
        self.groupName = None
        self.ipPermissions = []
        self.ownerId = None
        self.groupId = None
        self.ipPermissionsEgress = []
        self.tags = []
        self.vpcId = None


class IpPermission:
    def __init__(self):
        self.fromPort = None
        self.ipProtocol = None
        self.ipRanges = []
        self.ipv6Ranges = []
        self.prefixListIds = []
        self.toPort = None
        self.userIdGroupPairs = []


class IpRange:
    def __init__(self):
        self.cidrIp = None
        self.description = None


class Ipv6Range:
    def __init__(self):
        self.cidrIpv6 = None
        self.description = None


class PrefixListId:
    def __init__(self):
        self.description = None
        self.prefixListId = None


class UserIdGroupPair:
    def __init__(self):
        self.description = None
        self.groupId = None
        self.groupName = None
        self.peeringStatus = None
        self.userId = None
        self.vpcId = None
        self.vpcPeeringConnectionId = None


class IpPermissionsEgress:
    def __init__(self):
        self.fromPort = None
        self.ipProtocol = None
        self.ipRanges = []
        self.ipv6Ranges = []
        self.prefixListIds = []
        self.toPort = None
        self.userIdGroupPairs = []


class Tag:
    def __init__(self):
        self.key = None
        self.value = None

def get_security_groups(session):
    next_token = None
    security_groups = []

    client = session.client(service_name="ec2")

    while True:

        # If there is a token to continue getting records use it, otherwise retrieve the first set of records
        if next_token:
            response = client.describe_security_groups(NextToken=next_token)
        else:
            response = client.describe_security_groups()

        # Loop though each security group in the response
        for group in response.get("SecurityGroups"):

            # Create security group object and parse data from response
            sg = SecurityGroup()
            sg.description = group.get("Description")
            sg.groupName = group.get("GroupName")
            sg.ownerId = group.get("OwnerId")
            sg.groupId = group.get("GroupId")
            sg.vpcId = group.get("VpcId")

            if group.get("IpPermissions"):
                # Parse IpPermissions for the current item
                for permission in group.get("IpPermissions"):
                    ipp = IpPermission()
                    ipp.fromPort = permission.get("FromPort")
                    ipp.ipProtocol = permission.get("IpProtocol")
                    ipp.toPort = permission.get("ToPort")

                    # Parse IP Ranges
                    if permission.get("IpRanges"):
                        for ip_range in permission.get("IpRanges"):
                            ipr = IpRange()
                            ipr.cidrIp = ip_range.get("CidrIp")
                            ipr.description = ip_range.get("Description")
                            ipp.ipRanges.append(ipr)

                    # Parse IPv6 Ranges
                    if permission.get("Ipv6Ranges"):
                        for ip6_range in permission.get("Ipv6Ranges"):
                            ip6r = Ipv6Range()
                            ip6r.cidrIpv6 = ip6_range.get("CidrIpv6")
                            ip6r.description = ip6_range.get("Description")
                            ipp.ipv6Ranges.append(ip6r)

                    # Parse PrefixList Ids
                    if permission.get("PrefixListIds"):
                        for prefix_list in permission.get("PrefixListIds"):
                            plid = PrefixListId()
                            plid.prefixListId = prefix_list.get("PrefixListId")
                            plid.description = prefix_list.get("Description")
                            ipp.prefixListIds.append(plid)

                    # Pares UserId Group Pairs
                    if permission.get("UserIdGroupPairs"):
                        for group_pair in permission.get("UserIdGroupPairs"):
                            uigp = UserIdGroupPair()
                            uigp.description = group_pair.get("Description")
                            uigp.groupId = group_pair.get("GroupId")
                            uigp.groupName = group_pair.get("GroupName")
                            uigp.peeringStatus = group_pair.get("PeeringStatus")
                            uigp.userId = group_pair.get("UserId")
                            uigp.vpcId = group_pair.get("VpcId")
                            uigp.vpcPeeringConnectionId = group_pair.get("VpcPeeringConnectionId")
                            ipp.userIdGroupPairs.append(uigp)

                    # Add to the security group
                    sg.ipPermissions.append(ipp)

            if group.get("IpPermissionsEgress"):
                # Parse IpPermissionsEgress for the current item
                for permission in group.get("IpPermissionsEgress"):
                    ippe = IpPermissionsEgress()
                    ippe.fromPort = permission.get("FromPort")
                    ippe.ipProtocol = permission.get("IpProtocol")
                    ippe.toPort = permission.get("ToPort")

                    # Parse IP Ranges
                    if permission.get("IpRanges"):
                        for ip_range in permission.get("IpRanges"):
                            ipr = IpRange()
                            ipr.cidrIp = ip_range.get("CidrIp")
                            ipr.description = ip_range.get("Description")
                            ippe.ipRanges.append(ipr)

                    # Parse IPv6 Ranges
                    if permission.get("Ipv6Ranges"):
                        for ip6_range in permission.get("Ipv6Ranges"):
                            ip6r = Ipv6Range()
                            ip6r.cidrIpv6 = ip6_range.get("CidrIpv6")
                            ip6r.description = ip6_range.get("Description")
                            ippe.ipv6Ranges.append(ip6r)

                    # Parse PrefixList Ids
                    if permission.get("PrefixListIds"):
                        for prefix_list in permission.get("PrefixListIds"):
                            plid = PrefixListId()
                            plid.prefixListId = prefix_list.get("PrefixListId")
                            plid.description = prefix_list.get("Description")
                            ippe.prefixListIds.append(plid)

                    # Pares UserId Group Pairs
                    if permission.get("UserIdGroupPairs"):
                        for group_pair in permission.get("UserIdGroupPairs"):
                            uigp = UserIdGroupPair()
                            uigp.description = group_pair.get("Description")
                            uigp.groupId = group_pair.get("GroupId")
                            uigp.groupName = group_pair.get("GroupName")
                            uigp.peeringStatus = group_pair.get("PeeringStatus")
                            uigp.userId = group_pair.get("UserId")
                            uigp.vpcId = group_pair.get("VpcId")
                            uigp.vpcPeeringConnectionId = group_pair.get("VpcPeeringConnectionId")
                            ippe.userIdGroupPairs.append(uigp)

                    sg.ipPermissionsEgress.append(ippe)

            # Parse the tags
            if group.get("Tags"):
                for tag in group.get("Tags"):
                    t = Tag()
                    t.key = tag.get("Key")
                    t.value = tag.get("Value")
                    sg.tags.append(t)

            # Add the parsed security group to the list
            security_groups.append(sg)

        # Check if the response contains a next token, if it does then use it to get the next page of results,
        # if not exit the infinite loop
        if response.get("NextToken"):
            next_token = response.get("NextToken")
        else:
            break

    # Return the list of parsed security groups
    return security_groups


def format_report(session,sg_results):

    r = utils.ReportBuilder()
    header_name = "AWS Security Group Report"
    header = menu_builder.build_header(header_name, 20)
    divider = menu_builder.build_divider(header_name,padding=20)
    r.write(header)
    r.write("Account ID: " + aws_utils.get_current_account_id(session))
    r.newline()
    r.write("Results")
    r.write(divider)
    r.newline()

    for region, security_groups in sg_results.items():
        r.write(f"{region} | {aws_utils.get_region_friendly_name(session,region)}", 0)

        vpcs = []

        for vpc_sg in security_groups:
            vpcs.append(vpc_sg.vpcId)

        # Remove duplicates
        vpcs = list(set(vpcs))

        for vpc in vpcs:
            # Add the VPC ID to the report
            r.write(vpc, 1)

            # Pull out security groups in the current VPCs
            selected_sgs = [s for s in security_groups if s.vpcId == vpc]

            # Loop though the selected security groups
            for sg in selected_sgs:

                # Add Security group ID and Name to the report
                if sg.groupName is None:
                    r.write(sg.groupId, 2)
                else:
                    r.write(f'{sg.groupName}({sg.groupId})', 2)

                # Add description to the report
                if sg.description:
                    r.write(f'Description: {sg.description}', 3)
                else:
                    r.write('Description: No description available', 3)

                # Add the inbound header to the report
                r.write('Inbound', 3)

                if len(sg.ipPermissions) == 0:
                    r.write('NONE', 4)
                else:
                    for in_traffic in sg.ipPermissions:
                        for ip in in_traffic.ipRanges:
                            if in_traffic.ipProtocol == "-1":
                                if ip.description:
                                    r.write(f'[{in_traffic.ipProtocol}] All Ports: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] All Ports: {ip.cidrIp}', 4)
                            elif in_traffic.fromPort == in_traffic.toPort:
                                if ip.description:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort}: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort}: {ip.cidrIp}', 4)
                            else:
                                if ip.description:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort} - {in_traffic.toPort}: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort} - {in_traffic.toPort}: {ip.cidrIp}', 4)

                        for sg_ref in in_traffic.userIdGroupPairs:
                            if in_traffic.ipProtocol == "-1":
                                if sg_ref.description:
                                    r.write(f'[{in_traffic.ipProtocol}] All Ports: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] All Ports: {sg_ref.groupId}', 4)
                            elif in_traffic.fromPort == in_traffic.toPort:
                                if sg_ref.description:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort}: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort}: {sg_ref.groupId}', 4)
                            else:
                                if sg_ref.description:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort} - {in_traffic.toPort}: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{in_traffic.ipProtocol}] {in_traffic.fromPort} - {in_traffic.toPort}: {sg_ref.groupId}', 4)

                # Add the inbound header to the report
                r. write('Outbound', 3)

                if len(sg.ipPermissionsEgress) == 0:
                    r.write('NONE', 4)
                else:
                    for out_traffic in sg.ipPermissionsEgress:
                        if len(out_traffic.ipRanges) == 0:
                            r.write('NONE', 4)

                        for ip in out_traffic.ipRanges:
                            if out_traffic.ipProtocol == "-1":
                                if ip.description:
                                    r.write(f'[{out_traffic.ipProtocol}] All Ports: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] All Ports: {ip.cidrIp}', 4)
                            elif out_traffic.fromPort == out_traffic.toPort:
                                if ip.description:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort}: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort}: {ip.cidrIp}', 4)
                            else:
                                if ip.description:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort} - {out_traffic.toPort}: {ip.cidrIp} ({ip.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort} - {out_traffic.toPort}: {ip.cidrIp}', 4)

                        for sg_ref in out_traffic.userIdGroupPairs:
                            if out_traffic.ipProtocol == "-1":
                                if ip.description:
                                    r.write(f'[{out_traffic.ipProtocol}] All Ports: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] All Ports: {sg_ref.groupId}', 4)
                            elif out_traffic.fromPort == out_traffic.toPort:
                                if sg_ref.description:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort}: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort}: {sg_ref.groupId}', 4)
                            else:
                                if sg_ref.description:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort} - {out_traffic.toPort}: {sg_ref.groupId} ({sg_ref.description})', 4)
                                else:
                                    r.write(f'[{out_traffic.ipProtocol}] {out_traffic.fromPort} - {out_traffic.toPort}: {sg_ref.groupId}', 4)

                # Add the Tags header to the report
                r.write('Tags', 3)

                if len(sg.tags) == 0:
                    r.write('NONE', 4)
                else:
                    for tag in sg.tags:
                        if tag.key is not None and tag.value is not None:
                            r.write(f'{tag.key}:{tag.value}', 4)
                        elif tag.key is not None and tag.value is None:
                            r.write(f'{tag.key}:No Value', 4)

                r.newline()

    return str(r)


