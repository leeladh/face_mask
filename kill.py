import os
import argparse
parser = argparse.ArgumentParser(description = "Kill Script")
parser.add_argument("-u", "--meeting_id", type=str, metavar='', required=True, help="User id or username")
args = parser.parse_args()

pid = os.system('pgrep -f '+str(args.meeting_id))
print(args.meeting_id+" : "+str(pid))
os.system('pkill -9 -f '+str(args.meeting_id))