#!/bin/sh

print_to_file() {
	local string=$1
	#echo "$string" >> /app/log_health_check.txt
}

save_log=">> /app/log_health_check.txt"

cd /app
print_to_file "$(date "+%Y-%m-%d %H:%M:%S")"
if [ -f /app/.icloud_backup_data ]; then
        if ! pgrep -f "python icloud_back.py" > /dev/null
        then
                print_to_file "health check:will run python..."
                #python icloud_back.py&
        else
                print_to_file "is running!"
        fi
else
        print_to_file "no icloud_back_data!"
fi

exit 0