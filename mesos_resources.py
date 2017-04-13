__author__ = 'tkraus-m'

import sys
import json
import marathon
import mesos
import requests

'''
dcos_master = input("Enter the DNS hostname or IP of your Marathon Instance : ")
userid = input('Enter the username for the DCOS cluster : ')
password = input('Enter the password for the DCOS cluster : ')
'''
dcos_master = 'https://awsmaster'
userid = 'bootstrapuser'
password = 'deleteme'
## marathon_app_json = '/Users/tkraus/sandbox/marathon/12b-siege.json'


## Login to DCOS to retrieve an API TOKEN
dcos_token = marathon.dcos_auth_login(dcos_master,userid,password)
if dcos_token != '':
    # Change - Remove Token from printing
    print('{}{}'.format("DCOS TOKEN = ", dcos_token))
else:
    exit(1)
print('-----------------------------')


## MESOS SECTION
new_mesos = mesos.mesos(dcos_master,dcos_token)

mesos_stats_text = new_mesos.get_metrics()
# Change - Remove RAW print below.
print("DEBUG - RAW Mesos stats = " + mesos_stats_text)
mesos_stats_json = json.loads(mesos_stats_text)



# print(mesos_quota_json['infos'][0]['guarantee'])
#print(mesos_quota_json['infos'][0]['guarantee'][0]['scalar']['value'])
#print(mesos_quota_json['infos'][0]['guarantee'][1]['name'])
#print(mesos_quota_json['infos'][0]['guarantee'][1]['scalar']['value'])



#stuff['guarantee']['name'] + ' - ' + stuff['guarantee']['scalar']['value']   


print ("\n=======================================================")
print ("DCOS Cluster MESOS ROLES Information")
mesos_roles_json = json.loads(new_mesos.get_roles())
roles=[]
for role in mesos_roles_json['roles']:
    roles.append(role['name'])
roles.pop(0)
print(str(roles))

# Change - Please put the Mesos Agents at the END and keep all the Reservations, quotas, and Cluster wide information at the front.
# Change - Please remove the (u' from the printout) and just keep the KEY and Value in String format without the parenthesis.

print ("\n=======================================================")
print ("MESOS AGENTS Information")
mesos_agents_text = new_mesos.get_agents()
mesos_agents_json = json.loads(mesos_agents_text)


dict_for_totals_perRole={}
total_cpu_per_role=0
total_disk_per_role=0
total_mem_per_role=0
for agent in mesos_agents_json['slaves']:
    # "agent" is a dict object
    print('\n-----------------------------------------------------------------------------------------------------')
    print('{}: {}    {}: {}'.format('Agent ID',agent['id'],'Hostname',agent['hostname']))

    print(' {} = {}'.format('Configured CPU',int(agent.get('resources',{'cpus'})['cpus'])))
    print(' {} = {}'.format('Configured MEM',int(agent.get('resources',{'mem'})['mem'])))
    print(' {} = {}'.format('Configured DISK',int(agent.get('resources',{'disk'})['disk'])))
    print(' {} = {}'.format('Configured GPUs',int(agent.get('resources',{'gpus'})['gpus'])))

    reservations = agent['reserved_resources_full']
    # reservations is a python dict
    # print('{} ={}'.format('DEBUG - Full Agent Reserved Resources Full KEY', agent['reserved_resources_full'].items()))


    for key,value in agent['reserved_resources_full'].items():
        # Loop Through the "agent" dict
        print('-----------------------------')
        mesos_role = key
        print('{}  {}'.format('Mesos Role: ',mesos_role))
        role_cpus_total=0
        role_mem_total=0
        role_disk_total=0
        for reservation in value:
            # reservation is a dict
            resource_name=reservation.get('name')
            #resource_value=reservation.get('scalar',{'value'})['value']
            if reservation.get('name') == 'cpus':
                role_cpus_total=(role_cpus_total + reservation.get('scalar',{'value'})['value'])
		      # total_cpu_per_role = total_cpu_per_role + role_cpus_total

            if reservation.get('name') == 'mem':
                role_mem_total=(role_cpus_total + reservation.get('scalar',{'value'})['value'])
		      # total_mem_per_role = total_mem_per_role + role_mem_total		

            if reservation.get('name')=='disk':
                role_disk_total=(role_cpus_total + reservation.get('scalar',{'value'})['value'])
		      # total_disk_per_role = total_disk_per_role + role_disk_total

    #print('{} {} {} {} {}:'.format('Role',mesos_role,'on agent', agent['hostname'],'is using'))
    print('  {} = {}'.format('Reserved CPUS',role_cpus_total))
    if ('cpus-'+ mesos_role) in dict_for_totals_perRole:
        dict_for_totals_perRole['cpus-'+ mesos_role] += role_cpus_total
    else:
        dict_for_totals_perRole['cpus-'+ mesos_role] = role_cpus_total

    print('  {} = {}'.format('Reserved DISK',role_disk_total))
    if ('disk-'+ mesos_role) in dict_for_totals_perRole:
        dict_for_totals_perRole['disk-'+mesos_role] += role_disk_total
    else:
        dict_for_totals_perRole['disk-'+mesos_role] = role_disk_total
        
	# dict_for_totals_perRole[mesos_role+'- disk'] = role_disk_total
    print('  {} = {}'.format('Reserved MEM',role_mem_total))
    if ('mem-'+mesos_role) in dict_for_totals_perRole:
        dict_for_totals_perRole['mem-'+mesos_role] += role_mem_total
    else:
        dict_for_totals_perRole['mem-'+mesos_role] = role_mem_total
        
	# dict_for_totals_perRole[mesos_role+'- mem'] = role_mem_total


# print (" Following are the Reservations of CPU , DISK and MEM across the cluster ")
total_reserved_cpu=0
total_reserved_disk=0
total_reserved_mem=0



print ("Total Resources Summary ")
print ("\n=======================================================")
print ("MESOS Metrics Snapshot")
print ("MEMORY")
print('    {} = {} {}'.format('DCOS Mesos mem_total Configured', int(mesos_stats_json.get('master/mem_total')), 'MB'))
print('    {} = {} {}'.format('DCOS Mesos mem_used', mesos_stats_json.get('master/mem_used'), 'MB'))
print('    {} = {} {}'.format('DCOS Mesos mem_percent', round(mesos_stats_json.get('master/mem_percent')*100,2), '%'))
# print "    Reserved Mem is :{}".format(total_reserved_mem)

#print total_reserved_mem
#print('    {} = {} {}'.format('DCOS Mesos Reserved MEM',int(total_reserved_mem)))


print ("CPU")
print('    {} = {} {}'.format('DCOS Mesos cpu_total Configured', int(mesos_stats_json.get('master/cpus_total')), 'Cores'))
print('    {} = {} {}'.format('DCOS Mesos cpu_used', mesos_stats_json.get('master/cpus_used'), 'Cores'))
print('    {} = {} {}'.format('DCOS Mesos cpu_percent', round(mesos_stats_json.get('master/cpus_percent')*100,2), '%'))
# print('    {} = {} {}'.format('DCOS Mesos Reserved CPUs',total_reserved_cpu))
# print "     Reserved CPU is :{}".format(total_reserved_cpu)

print ("DISK")
print('    {} = {} {}'.format('DCOS Mesos disk_total Configured', int(mesos_stats_json.get('master/disk_total')), 'MB'))
print('    {} = {} {}'.format('DCOS Mesos disk_used', int(mesos_stats_json.get('master/disk_used')), 'MB'))
print('    {} = {} {}'.format('DCOS Mesos disk_percent', round(mesos_stats_json.get('master/disk_percent')*100,2), '%'))
# print('    {} = {} {}'.format('DCOS Mesos Reserved DISK',total_reserved_disk))
# print "      Reserved Disk is :{}".format(total_reserved_disk)

print ("\n=======================================================")
 
print ("Reservations Informtion is as follows :\n")

print ("Breakup by Role - \n")
for key_resource, value_resource in dict_for_totals_perRole.iteritems():
	if key_resource.startswith('cpu'):
		total_reserved_cpu = total_reserved_cpu + value_resource
	if key_resource.startswith('disk'):
		total_reserved_disk += value_resource
	if key_resource.startswith('mem'):
		total_reserved_mem += value_resource

	print (key_resource, value_resource)

print ("Total Reservations by Resource \n")
print ("    Reserved Mem is :{}".format(total_reserved_mem))
print ("    Reserved CPU is :{}".format(total_reserved_cpu))
print ("    Reserved Disk is :{}".format(total_reserved_disk))

print ("\n=======================================================")

print ("\n Quota information by role is as follows:\n")
#f
mesos_quota_text = new_mesos.get_quota_info()

mesos_quota_json =  json.loads(mesos_quota_text)

if mesos_quota_json:
	for d1 in mesos_quota_json['infos']:
		print d1['role'] + ' : '
		for d2 in d1['guarantee']:
			print d2['name'] + ' - ' + str(d2['scalar']['value'])   
		print "\n"
else: 
	print ("Quota have not been set") 


print ("\n=======================================================")


print ("  FRAMEWORKS")
print('    {} = {} '.format('DCOS Mesos Connected Frameworks', int(mesos_stats_json.get('master/frameworks_connected'))))
print('    {} = {} '.format('DCOS Mesos Active Frameworks', int(mesos_stats_json.get('master/frameworks_active'))))

print ("\n=======================================================")

print ("  AGENTS")
print('    {} = {} '.format('DCOS Mesos Active Agents', int(mesos_stats_json.get('master/slaves_active'))))
print('    {} = {} '.format('DCOS Mesos Connected Agents', int(mesos_stats_json.get('master/slaves_connected'))))

print ("\n=======================================================")
	
	


