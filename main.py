#!/usr/bin/env python3
"""
Windows Water Reminder
Persistent notifications using Windows Task Scheduler
"""

import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from plyer import notification
except ImportError:
    print("plyer not found. Install it with: pip install plyer")
    sys.exit(1)

class WaterReminder:
    def __init__(self, config_file="water_reminder_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "interval_minutes": 60,
            "start_time": "08:00",
            "end_time": "22:00",
            "message": "💧 Time to drink water! Stay hydrated! 💧",
            "title": "Water Reminder",
            "sound_enabled": True,
            "last_reminder": None
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def send_notification(self):
        """Send water reminder notification"""
        try:
            notification.notify(
                title=self.config["title"],
                message=self.config["message"],
                app_name="Water Reminder",
                timeout=10
            )
            print(f"Notification sent at {datetime.now().strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def is_within_active_hours(self):
        """Check if current time is within active hours"""
        now = datetime.now().time()
        start_time = datetime.strptime(self.config["start_time"], "%H:%M").time()
        end_time = datetime.strptime(self.config["end_time"], "%H:%M").time()
        
        return start_time <= now <= end_time
    
    def run_continuous(self):
        """Run reminder continuously (requires program to stay running)"""
        print(f"Water reminder started!")
        print(f"Interval: {self.config['interval_minutes']} minutes")
        print(f"Active hours: {self.config['start_time']} - {self.config['end_time']}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                if self.is_within_active_hours():
                    self.send_notification()
                    self.config["last_reminder"] = datetime.now().isoformat()
                    self.save_config()
                
                time.sleep(self.config["interval_minutes"] * 60)
                
        except KeyboardInterrupt:
            print("\nWater reminder stopped.")
    
    def create_task_scheduler_batch(self):
        """Create batch file for Windows Task Scheduler"""
        script_content = f'''@echo off
cd /d "{os.path.dirname(os.path.abspath(__file__))}"
python "{os.path.abspath(__file__)}" --notify
'''
        
        script_path = "water_reminder_task.bat"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Created batch script: {script_path}")
        return os.path.abspath(script_path)
    
    def create_task_scheduler_xml(self, batch_path):
        """Create XML file for Task Scheduler import"""
        xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-01-01T12:00:00</Date>
    <Author>Water Reminder</Author>
    <Description>Reminds you to drink water regularly</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT{self.config['interval_minutes']}M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2024-01-01T{self.config['start_time']}:00</StartBoundary>
      <EndBoundary>2024-01-01T{self.config['end_time']}:00</EndBoundary>
      <ExecutionTimeLimit>PT1M</ExecutionTimeLimit>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{batch_path}</Command>
      <WorkingDirectory>{os.path.dirname(batch_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        xml_path = "WaterReminder_Task.xml"
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_content)
        
        print(f"✅ Created Task Scheduler XML: {xml_path}")
        return os.path.abspath(xml_path)
    
    def setup_task_scheduler(self):
        """Setup Windows Task Scheduler with complete instructions"""
        print("🔧 Setting up Windows Task Scheduler...")
        print("=" * 50)
        
        # Create batch file
        batch_path = self.create_task_scheduler_batch()
        
        # Create XML file for easy import
        xml_path = self.create_task_scheduler_xml(batch_path)
        
        print("\n📋 SETUP INSTRUCTIONS:")
        print("=" * 30)
        
        print("\n🎯 METHOD 1 - Easy Import (Recommended):")
        print("1. Press Win + R, type 'taskschd.msc' and press Enter")
        print("2. In Task Scheduler, click 'Import Task...' in the right panel")
        print(f"3. Browse and select: {xml_path}")
        print("4. Click 'OK' to import the task")
        print("5. The task 'WaterReminder_Task' will be created automatically!")
        
        print("\n🔧 METHOD 2 - Manual Setup:")
        print("1. Press Win + R, type 'taskschd.msc' and press Enter")
        print("2. Click 'Create Basic Task...' in the right panel")
        print("3. Name: 'Water Reminder'")
        print("4. Trigger: Select 'Daily'")
        print("5. Start time: Set to your preferred start time")
        print("6. Action: 'Start a program'")
        print(f"7. Program/script: {batch_path}")
        print("8. In Advanced settings:")
        print(f"   - Check 'Repeat task every: {self.config['interval_minutes']} minutes'")
        print(f"   - For a duration of: 14 hours (or your active period)")
        print("9. Click 'Finish'")
        
        print("\n✅ VERIFICATION:")
        print("- You can test the task by right-clicking it and selecting 'Run'")
        print("- Check 'Task Scheduler Library' to see your created task")
        print("- The task will run automatically based on your schedule")
        
        print(f"\n⚙️  CURRENT SETTINGS:")
        print(f"- Interval: Every {self.config['interval_minutes']} minutes")
        print(f"- Active hours: {self.config['start_time']} to {self.config['end_time']}")
        print(f"- Message: {self.config['message']}")
        
        print(f"\n📁 FILES CREATED:")
        print(f"- Batch file: {batch_path}")
        print(f"- XML file: {xml_path}")
        print(f"- Config file: {os.path.abspath(self.config_file)}")
    
    def check_task_scheduler_status(self):
        """Check if task is set up in Windows Task Scheduler"""
        try:
            import subprocess
            result = subprocess.run([
                'schtasks', '/query', '/tn', 'WaterReminder_Task'
            ], capture_output=True, text=True, shell=True)
            return result.returncode == 0
        except:
            return False
    
    def get_status_info(self):
        """Get current status information"""
        batch_exists = os.path.exists("water_reminder_task.bat")
        xml_exists = os.path.exists("WaterReminder_Task.xml")
        task_exists = self.check_task_scheduler_status()
        
        status = {
            'files_created': batch_exists and xml_exists,
            'task_scheduled': task_exists,
            'last_reminder': self.config.get('last_reminder'),
            'is_active_time': self.is_within_active_hours()
        }
        
        return status
        """Check if reminder is due (for scheduled execution)"""
        if not self.config.get("last_reminder"):
            return True
        
        last_reminder = datetime.fromisoformat(self.config["last_reminder"])
        time_since_last = datetime.now() - last_reminder
        interval_seconds = self.config["interval_minutes"] * 60
        
        return time_since_last.total_seconds() >= interval_seconds
    
    def configure(self):
        """Interactive configuration"""
        print("=== Water Reminder Configuration ===")
        
        # Interval
        current_interval = self.config["interval_minutes"]
        new_interval = input(f"Reminder interval in minutes (current: {current_interval}): ")
        if new_interval.strip():
            try:
                self.config["interval_minutes"] = int(new_interval)
            except ValueError:
                print("Invalid interval, keeping current value")
        
        # Active hours
        print(f"Current active hours: {self.config['start_time']} - {self.config['end_time']}")
        new_start = input("Start time (HH:MM, or press Enter to keep current): ")
        if new_start.strip():
            self.config["start_time"] = new_start
        
        new_end = input("End time (HH:MM, or press Enter to keep current): ")
        if new_end.strip():
            self.config["end_time"] = new_end
        
        # Message
        print(f"Current message: {self.config['message']}")
        new_message = input("New message (or press Enter to keep current): ")
        if new_message.strip():
            self.config["message"] = new_message
        
        self.save_config()
        print("✅ Configuration saved!")
        print("\n⚠️  Note: If you already set up Task Scheduler, you may need to")
        print("update the task or recreate it to use the new settings.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows Water Reminder App')
    parser.add_argument('--notify', action='store_true', 
                       help='Send notification (for scheduled execution)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously')
    parser.add_argument('--configure', action='store_true',
                       help='Configure settings')
    parser.add_argument('--setup', action='store_true',
                       help='Setup Windows Task Scheduler')
    
    args = parser.parse_args()
    
    reminder = WaterReminder()
    
    if args.notify:
        # Single notification (for Task Scheduler execution)
        if reminder.is_within_active_hours() and reminder.check_reminder_due():
            if reminder.send_notification():
                reminder.config["last_reminder"] = datetime.now().isoformat()
                reminder.save_config()
    
    elif args.continuous:
        # Continuous mode
        reminder.run_continuous()
    
    elif args.configure:
        # Configuration mode
        reminder.configure()
    
    elif args.setup:
        # Setup Task Scheduler
        reminder.setup_task_scheduler()
    
    else:
        # Check if Task Scheduler is already set up
        batch_exists = os.path.exists("water_reminder_task.bat")
        xml_exists = os.path.exists("WaterReminder_Task.xml")
        
        print("🚰 === Windows Water Reminder ===")
        
        # Check if Task Scheduler is already set up
        status = reminder.get_status_info()
        
        print("🚰 === Windows Water Reminder ===")
        
        if status['files_created']:
            print("📊 STATUS:")
            print(f"✅ Setup files: Created")
            print(f"{'✅' if status['task_scheduled'] else '❌'} Task Scheduler: {'Active' if status['task_scheduled'] else 'Not found'}")
            
            if status['last_reminder']:
                last_time = datetime.fromisoformat(status['last_reminder']).strftime('%H:%M:%S')
                print(f"🕒 Last reminder: {last_time}")
            
            print(f"⏰ Currently {'ACTIVE' if status['is_active_time'] else 'INACTIVE'} (Active: {reminder.config['start_time']}-{reminder.config['end_time']})")
            print()
            
            if status['task_scheduled']:
                print("🎉 Your water reminder is running automatically!")
                print("1. Send test notification")
                print("2. Configure settings") 
                print("3. View detailed status")
                print("4. Re-setup Task Scheduler")
                print("5. Run continuously (manual mode)")
                print("6. Exit")
                
                choice = input("Choose option (1-6): ")
                
                if choice == "1":
                    if reminder.send_notification():
                        print("✅ Test notification sent!")
                    else:
                        print("❌ Failed to send notification")
                elif choice == "2":
                    reminder.configure()
                elif choice == "3":
                    reminder.show_detailed_status()
                elif choice == "4":
                    reminder.setup_task_scheduler()
                elif choice == "5":
                    reminder.run_continuous()
                elif choice == "6":
                    print("Goodbye! Stay hydrated! 💧")
                else:
                    print("Invalid choice")
            else:
                print("⚠️  Task Scheduler task not found. You may need to set it up.")
                print("1. Setup Task Scheduler")
                print("2. Send test notification")
                print("3. Configure settings")
                print("4. Run continuously (manual mode)")
                print("5. Exit")
                
                choice = input("Choose option (1-5): ")
                
                if choice == "1":
                    reminder.setup_task_scheduler()
                elif choice == "2":
                    if reminder.send_notification():
                        print("✅ Test notification sent!")
                    else:
                        print("❌ Failed to send notification")
                elif choice == "3":
                    reminder.configure()
                elif choice == "4":
                    reminder.run_continuous()
                elif choice == "5":
                    print("Goodbye! Stay hydrated! 💧")
                else:
                    print("Invalid choice")
        else:
            print("🚀 Welcome! Let's set up your water reminder.")
            print("1. Setup Task Scheduler (recommended - works in background)")
            print("2. Run continuously (keep program running)")
            print("3. Configure settings first")
            print("4. Send test notification")
            print("5. Exit")
            
            choice = input("Choose option (1-5): ")
            
            if choice == "1":
                reminder.setup_task_scheduler()
            elif choice == "2":
                reminder.run_continuous()
            elif choice == "3":
                reminder.configure()
            elif choice == "4":
                if reminder.send_notification():
                    print("✅ Test notification sent!")
                else:
                    print("❌ Failed to send notification")
            elif choice == "5":
                print("Goodbye! Stay hydrated! 💧")
            else:
                print("Invalid choice")


if __name__ == "__main__":
    main()