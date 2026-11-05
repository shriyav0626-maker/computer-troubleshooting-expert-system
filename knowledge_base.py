"""
knowledge_base.py
Knowledge base for the Computer Troubleshooting Expert System.

Contains:
  CATEGORIES - the 10 problem categories shown on the home page
  QUESTIONS  - diagnostic questions (facts the user can answer)
  RULES      - IF-THEN rules:  IF all conditions match THEN cause + steps

This is a rule-based (knowledge-based) AI system. It is NOT machine learning.
"""

ANSWERS = ("yes", "no", "unsure")

DISCLAIMER = (
    "This is a rule-based expert system. Its suggestions are possible causes, "
    "not guaranteed diagnoses. If a problem continues, contact a qualified technician."
)

FALLBACK_STEPS = [
    "Restart the computer and check whether the problem is still there.",
    "Check that all cables, chargers, and connected devices are firmly attached.",
    "Note any error messages exactly as they appear (a phone photo helps).",
    "Search the manufacturer's support website using your model number and the error message.",
    "If the problem continues or you feel unsure, contact a qualified technician. "
    "Do not open the computer or its power supply yourself.",
]

CATEGORIES = [
    {"id": "no_power", "title": "Computer does not turn on", "icon": "⚡",
     "description": "Nothing happens when you press the power button."},
    {"id": "no_boot", "title": "Computer turns on but does not boot", "icon": "🖥️",
     "description": "It powers up, but Windows never loads."},
    {"id": "slow", "title": "Computer is running slowly", "icon": "🐢",
     "description": "Programs lag, freeze, or take long to open."},
    {"id": "internet", "title": "Internet is not working", "icon": "🌐",
     "description": "No Wi-Fi, no websites, or 'No Internet' warnings."},
    {"id": "overheating", "title": "Computer is overheating", "icon": "🔥",
     "description": "Very hot, loud fans, or shutting down from heat."},
    {"id": "crashes", "title": "Blue screen or frequent crashes", "icon": "💥",
     "description": "Blue error screens or unexpected restarts."},
    {"id": "sound", "title": "No sound from speakers or headphones", "icon": "🔊",
     "description": "Audio is silent or very quiet."},
    {"id": "input", "title": "Keyboard or mouse is not working", "icon": "⌨️",
     "description": "Keys, cursor, or touchpad do not respond."},
    {"id": "app_hang", "title": "Application is not responding", "icon": "🧩",
     "description": "A program freezes or shows 'Not Responding'."},
    {"id": "printer", "title": "Printer is not working", "icon": "🖨️",
     "description": "Documents do not print or the printer is not found."},
]

QUESTIONS = {}   # question id -> {"id", "category", "text"}  (insertion order = ask order)
RULES = []       # list of rule dictionaries


def _q(qid, category, text):
    QUESTIONS[qid] = {"id": qid, "category": category, "text": text}


def _r(rule_id, category, conditions, cause, priority, confidence, steps, urgent=False):
    RULES.append({
        "id": rule_id,
        "category": category,
        "conditions": conditions,   # {question_id: "yes" or "no"}
        "cause": cause,
        "priority": priority,       # higher = more specific / more important
        "confidence": confidence,   # "High", "Medium" or "Low" (strength of the rule)
        "steps": steps,
        "urgent": urgent,           # True = safety warning
    })


# ---------------------------------------------------------------- 1. NO POWER
_q("np_burn", "no_power", "Do you notice smoke, a burning smell, or a swollen/bulging battery or case?")
_q("np_light", "no_power", "When you press the power button, does anything happen at all (a light turns on, a fan spins, or you hear a sound)?")
_q("np_cable", "no_power", "Have you confirmed the power cable or charger is firmly plugged in and the wall socket works (for example, by testing another device in it)?")
_q("np_laptop", "no_power", "Is this a laptop (rather than a desktop)?")
_q("np_beeps", "no_power", "Does the computer beep, or start for a moment and then shut off by itself?")

_r("NP1", "no_power", {"np_burn": "yes"},
   "Possible electrical or battery damage", 100, "High", [
       "Stop using the computer right away.",
       "If it is safe to do so, shut it down and unplug the power cable and charger.",
       "Do not open the case or touch damaged parts, and keep it away from flammable items.",
       "Do not charge or turn on a swollen battery. Take it to a qualified technician or the manufacturer's service centre.",
   ], urgent=True)
_r("NP2", "no_power", {"np_burn": "no", "np_light": "no", "np_cable": "no"},
   "Power cable, charger, or wall socket problem", 50, "High", [
       "Push the power cable firmly into both the computer and the wall socket.",
       "Try a different wall socket and test it with another device.",
       "If you use a power strip, plug the computer directly into the wall instead.",
       "If you have a spare compatible cable or charger, try it.",
       "Wait one minute, then press the power button once.",
   ])
_r("NP3", "no_power", {"np_burn": "no", "np_light": "no", "np_cable": "yes", "np_laptop": "no"},
   "Failed power supply or power button connection (desktop)", 40, "Medium", [
       "Check the small switch on the back of the computer (near the power cable) is set to I (on).",
       "Unplug the cable, wait 30 seconds, plug it back in, and try again.",
       "Disconnect extra devices such as USB drives and printers, then try again.",
       "Do not open the power supply unit. If nothing works, take it to a qualified technician.",
   ])
_r("NP4", "no_power", {"np_burn": "no", "np_light": "no", "np_cable": "yes", "np_laptop": "yes"},
   "Faulty charger or fully drained battery (laptop)", 40, "Medium", [
       "Leave the charger connected for 30 minutes, then try to turn the laptop on.",
       "Check the charger cable for visible damage; try a compatible charger if you have one.",
       "Disconnect all USB and external devices.",
       "If it still does not start, take it to a qualified repair service.",
   ])
_r("NP5", "no_power", {"np_burn": "no", "np_light": "yes", "np_beeps": "yes"},
   "Hardware fault found at startup (for example memory or graphics)", 40, "Medium", [
       "Turn it off, then unplug USB drives, printers, and other external devices.",
       "Restart and count the beeps; note the pattern.",
       "Look up the beep pattern in the manual or on the manufacturer's website.",
       "If you are unsure, do not open the case; ask a qualified technician to check the components.",
   ])

# ---------------------------------------------------------------- 2. NO BOOT
_q("nb_noise", "no_boot", "Do you hear repeated clicking, grinding, or scraping noises from inside the computer?")
_q("nb_error", "no_boot", "Does the screen show an error such as 'No bootable device', 'Operating system not found', or 'Boot device not found'?")
_q("nb_usb", "no_boot", "Is a USB drive, external disk, or disc currently connected to the computer?")
_q("nb_logo", "no_boot", "Does the manufacturer or Windows logo appear, then the computer restarts repeatedly, hangs, or shows a repair screen?")

_r("NB1", "no_boot", {"nb_noise": "yes"},
   "Possible failing hard drive", 60, "Medium", [
       "Turn the computer off. Repeated attempts to start it can make a failing drive worse.",
       "Do not try to repair it yourself or run tools that rewrite the drive.",
       "If you have important files, take the computer to a data-recovery or repair professional as soon as possible.",
       "A failed drive usually needs to be replaced, followed by reinstalling Windows.",
   ])
_r("NB2", "no_boot", {"nb_noise": "no", "nb_error": "yes", "nb_usb": "yes"},
   "Computer is trying to start from a connected USB drive or disc", 50, "High", [
       "Turn off the computer.",
       "Remove all USB drives, external disks, memory cards, and discs.",
       "Turn the computer on again and see whether Windows starts.",
   ])
_r("NB3", "no_boot", {"nb_noise": "no", "nb_error": "yes", "nb_usb": "no"},
   "Boot drive not detected, or startup files damaged", 40, "Medium", [
       "Restart and read the error message again.",
       "Open the BIOS/UEFI setup (often by pressing Del, F2, or F10 at startup) and check whether your drive is listed. Do not change other settings.",
       "If the drive is not listed, it may be loose or failed; ask a technician to check it.",
       "If it is listed, run Startup Repair from Windows installation media. Avoid 'Reset this PC' or reinstalling unless your files are backed up, because they can erase data.",
   ])
_r("NB4", "no_boot", {"nb_noise": "no", "nb_error": "no", "nb_logo": "yes"},
   "Windows startup files damaged (for example after an update or sudden shutdown)", 40, "Medium", [
       "Let the computer try Automatic Repair if it appears.",
       "In the recovery menu choose Troubleshoot > Advanced options > Startup Repair.",
       "If that fails, try Uninstall Updates, System Restore, or Safe Mode from the same menu.",
       "Avoid 'Reset this PC' unless your files are backed up; it can remove programs and files.",
   ])

# ---------------------------------------------------------------- 3. SLOW
_q("sl_malware", "slow", "Do you see unexpected pop-ups, unfamiliar toolbars or programs, or a changed browser homepage?")
_q("sl_disk", "slow", "Is your main drive (usually C:) almost full, with less than 10% free space?")
_q("sl_ram", "slow", "Open Task Manager (Ctrl + Shift + Esc). Is Memory usage above 85% most of the time?")
_q("sl_cpu", "slow", "In Task Manager, is one program using most of the CPU or Disk all the time?")
_q("sl_startup", "slow", "Is the computer slowest right after starting up, with many programs opening by themselves?")

_r("SL1", "slow", {"sl_malware": "yes"},
   "Possible unwanted software or malware", 55, "Medium", [
       "Run a full scan with Windows Security (Virus & threat protection).",
       "Uninstall programs you do not recognise from Settings > Apps.",
       "Do not download 'free cleaner' tools from pop-ups or ads.",
       "If a scan finds threats, follow its instructions and change important passwords afterwards.",
   ])
_r("SL2", "slow", {"sl_malware": "no", "sl_disk": "yes"},
   "Storage drive is almost full", 50, "High", [
       "Open Settings > System > Storage to see what uses the space.",
       "Run Storage Sense or Disk Cleanup, and read what each item removes before confirming.",
       "Uninstall programs you no longer use.",
       "Move large personal files (photos, videos) to an external drive instead of deleting them. Never delete system files you do not recognise.",
   ])
_r("SL3", "slow", {"sl_malware": "no", "sl_disk": "no", "sl_ram": "yes"},
   "Not enough memory (RAM) for the current workload", 45, "Medium", [
       "Close programs and browser tabs you do not need.",
       "Restart the computer to free up memory.",
       "Check in Task Manager which apps use the most memory.",
       "If memory is always high, ask a technician whether adding RAM is possible.",
   ])
_r("SL4", "slow", {"sl_malware": "no", "sl_disk": "no", "sl_ram": "no", "sl_cpu": "yes"},
   "One program or background process is using too many resources", 45, "Medium", [
       "In Task Manager, note which program uses the resources.",
       "Save your work, select that program, and click End task. Do not end Windows system processes you do not recognise.",
       "Check for updates for that program, or reinstall it.",
       "If the process is unfamiliar, scan with Windows Security.",
   ])
_r("SL5", "slow", {"sl_malware": "no", "sl_disk": "no", "sl_ram": "no", "sl_cpu": "no", "sl_startup": "yes"},
   "Too many programs starting with Windows", 30, "Medium", [
       "Open Task Manager > Startup apps.",
       "Disable apps you do not need at startup. This does not uninstall them, and you can turn them on again later.",
       "Restart and compare the startup speed.",
       "Keep Windows and drivers up to date.",
   ])

# ---------------------------------------------------------------- 4. INTERNET
_q("in_airplane", "internet", "Is Airplane mode turned on, or is Wi-Fi switched off on your computer?")
_q("in_other", "internet", "Can other devices (like a phone) on the same network open websites normally?")
_q("in_connected", "internet", "Does your computer show that it is connected to the network (Wi-Fi or Ethernet), even if it says 'No Internet'?")
_q("in_sites", "internet", "Do some websites open while others do not?")

_r("IN1", "internet", {"in_airplane": "yes"},
   "Wi-Fi is switched off or Airplane mode is on", 60, "High", [
       "Click the network icon in the taskbar and turn Airplane mode off.",
       "Turn Wi-Fi on. Some laptops have a Wi-Fi key (often Fn plus a function key).",
       "Select your network and enter the password if asked.",
   ])
_r("IN2", "internet", {"in_airplane": "no", "in_other": "no"},
   "Router/modem problem or internet service outage", 50, "High", [
       "Check that the router lights are normal and the cables are firmly connected.",
       "Turn the router off, wait 30 seconds, turn it on, and wait about 2 minutes.",
       "Using mobile data, check whether your internet provider reports an outage.",
       "Contact your provider if the internet light stays red or off. Do not factory-reset the router, because that erases its settings and password.",
   ])
_r("IN3", "internet", {"in_airplane": "no", "in_other": "yes", "in_connected": "no"},
   "Computer's Wi-Fi/network adapter or connection problem", 45, "Medium", [
       "Restart the computer.",
       "Turn Wi-Fi off and on again, or unplug and re-plug the Ethernet cable.",
       "Forget the network (Settings > Network > Wi-Fi > Manage known networks) and reconnect with the password.",
       "Run the Windows network troubleshooter and update the network driver if needed.",
   ])
_r("IN4", "internet", {"in_airplane": "no", "in_other": "yes", "in_connected": "yes", "in_sites": "yes"},
   "Website-specific, DNS, or browser problem", 40, "Medium", [
       "Check on your phone whether the failing sites are down for everyone.",
       "Try a different browser.",
       "Clear the browser cache for those sites (this may sign you out).",
       "Open Command Prompt and run: ipconfig /flushdns",
   ])
_r("IN5", "internet", {"in_airplane": "no", "in_other": "yes", "in_connected": "yes", "in_sites": "no"},
   "Computer-level IP/DNS, VPN, proxy, or firewall problem", 35, "Low", [
       "Turn off any VPN or proxy and test again.",
       "Open Command Prompt and run: ipconfig /release and then ipconfig /renew",
       "Restart the computer.",
       "Use 'Network reset' (Settings > Network > Advanced) only as a last resort, since it removes saved networks and settings.",
   ])

# ---------------------------------------------------------------- 5. OVERHEATING
_q("oh_smoke", "overheating", "Do you notice smoke, a burning smell, or a swollen/bulging battery or case?")
_q("oh_dust", "overheating", "Are the vents or fan grills dusty or blocked, or is the computer on a bed, blanket, lap, or other soft surface?")
_q("oh_nofan", "overheating", "Can you hear or feel no fan running at all, even though the computer is hot?")
_q("oh_heavy", "overheating", "Does it mainly get hot during heavy tasks such as gaming, video editing, or many programs at once?")

_r("OH1", "overheating", {"oh_smoke": "yes"},
   "Possible overheating damage or battery hazard", 100, "High", [
       "Shut the computer down immediately and unplug the power cable only if it is safe to do so.",
       "Do not touch hot, damaged, or swollen parts, and do not charge it.",
       "Do not open the case.",
       "Move it to a hard, non-flammable surface and contact a qualified technician. If you see flames or heavy smoke, leave the area and call emergency services.",
   ], urgent=True)
_r("OH2", "overheating", {"oh_smoke": "no", "oh_dust": "yes"},
   "Blocked airflow or dust buildup", 50, "High", [
       "Shut down and let the computer cool for 15 to 20 minutes.",
       "Place it on a hard, flat surface; raise the back of a laptop for airflow.",
       "Gently blow dust out of the outside vents with short bursts of compressed air.",
       "Do not open the case unless you know how. Avoid household vacuum cleaners because they can create static electricity.",
   ])
_r("OH3", "overheating", {"oh_smoke": "no", "oh_dust": "no", "oh_nofan": "yes"},
   "Cooling fan not working", 50, "Medium", [
       "Shut down the computer to avoid damage.",
       "Do not keep using it until the cooling has been checked.",
       "Take it to a qualified technician for fan inspection or replacement.",
   ])
_r("OH4", "overheating", {"oh_smoke": "no", "oh_dust": "no", "oh_nofan": "no", "oh_heavy": "yes"},
   "Heavy workload producing a lot of heat", 35, "Medium", [
       "Close programs you do not need; lower graphics settings in games.",
       "Use a laptop cooling pad or improve ventilation in the room.",
       "Set the Windows power mode to Balanced.",
       "If it still shuts down or gets extremely hot, stop using it and seek professional service.",
   ])

# ---------------------------------------------------------------- 6. CRASHES
_q("bs_new", "crashes", "Did the crashes begin after installing new hardware, a driver, or a Windows update?")
_q("bs_heat", "crashes", "Does it mostly crash when the computer is hot or under heavy load (games, video editing)?")
_q("bs_disk", "crashes", "Do you also notice file errors, very slow file opening, or clicking sounds?")
_q("bs_random", "crashes", "Does it crash randomly, even when idle, with a different error message each time?")

_r("BS1", "crashes", {"bs_new": "yes"},
   "Faulty or incompatible driver, update, or new hardware", 50, "Medium", [
       "Write down the error name or stop code on the blue screen (a phone photo works well).",
       "Disconnect any newly added hardware and test again.",
       "In Device Manager, open the device's Properties > Driver > Roll Back Driver, if the button is available.",
       "Uninstall a recent update only if the problem started right after it. Updates can include security fixes, so reinstall it later if a fix is released.",
   ])
_r("BS2", "crashes", {"bs_new": "no", "bs_heat": "yes"},
   "Overheating causing crashes", 45, "Medium", [
       "Shut down and let the computer cool.",
       "Clean the outside vents and use a hard, flat surface.",
       "Avoid heavy tasks until the temperature problem is fixed.",
       "See the 'Computer is overheating' category for more checks.",
   ])
_r("BS3", "crashes", {"bs_new": "no", "bs_heat": "no", "bs_disk": "yes"},
   "Possible failing drive or corrupted system files", 45, "Medium", [
       "Back up important files to an external drive as soon as possible.",
       "Open Command Prompt as administrator and run: sfc /scannow",
       "Right-click the drive in File Explorer > Properties > Tools > Check.",
       "If you hear clicking noises, power off and get professional help.",
   ])
_r("BS4", "crashes", {"bs_new": "no", "bs_heat": "no", "bs_disk": "no", "bs_random": "yes"},
   "Possible faulty memory (RAM)", 40, "Low", [
       "Save your work, then search for 'Windows Memory Diagnostic' and run it (the computer restarts).",
       "If errors are reported, ask a technician to test or replace the memory.",
       "If no errors are found, run Windows Update and update your drivers.",
   ])

# ---------------------------------------------------------------- 7. SOUND
_q("so_mute", "sound", "Is the volume muted or very low (check the speaker icon, keyboard volume keys, and any knob on external speakers)?")
_q("so_conn", "sound", "Are the speakers or headphones correctly connected (right port, or paired by Bluetooth) and switched on?")
_q("so_other", "sound", "Do the same speakers or headphones work on another device such as a phone?")
_q("so_output", "sound", "In Windows sound settings, is the correct speaker or headphone device selected as the output?")

_r("SO1", "sound", {"so_mute": "yes"},
   "Volume is muted or too low", 55, "High", [
       "Click the speaker icon in the taskbar and raise the volume; unmute if needed.",
       "Check the volume knob or switch on external speakers.",
       "Open the Volume mixer and make sure the app is not muted.",
   ])
_r("SO2", "sound", {"so_mute": "no", "so_conn": "no"},
   "Speakers or headphones not properly connected", 50, "High", [
       "Push the audio cable in firmly (on desktops, use the green port for speakers).",
       "For Bluetooth devices, remove the device and pair it again.",
       "Make sure external speakers are powered on.",
   ])
_r("SO3", "sound", {"so_mute": "no", "so_conn": "yes", "so_other": "no"},
   "Faulty speakers, headphones, or cable", 45, "Medium", [
       "Try a different pair of speakers or headphones.",
       "Try a different cable or port.",
       "Replace the device if it fails on every device you try.",
   ])
_r("SO4", "sound", {"so_mute": "no", "so_conn": "yes", "so_other": "yes", "so_output": "no"},
   "Wrong audio output device selected", 45, "High", [
       "Right-click the speaker icon and open Sound settings.",
       "Under Output, choose your speakers or headphones.",
       "Play a sound to test it.",
   ])
_r("SO5", "sound", {"so_mute": "no", "so_conn": "yes", "so_other": "yes", "so_output": "yes"},
   "Audio driver, Windows audio service, or app-specific sound problem", 35, "Medium", [
       "Check whether the sound is missing in only one app or browser tab; if so, check that app's volume and mute settings.",
       "Run Settings > System > Sound > Troubleshoot.",
       "Restart the computer.",
       "Update or reinstall the audio driver from Device Manager or the manufacturer's website.",
   ])

# ---------------------------------------------------------------- 8. KEYBOARD / MOUSE
_q("km_builtin", "input", "Is the problem with the built-in keyboard or touchpad of a laptop?")
_q("km_wireless", "input", "Is the keyboard or mouse wireless (Bluetooth or USB receiver)?")
_q("km_battery", "input", "Are the batteries fresh or charged, and is the device switched on?")

_r("KM1", "input", {"km_builtin": "yes"},
   "Disabled device, driver problem, or hardware fault in the built-in keyboard/touchpad", 40, "Medium", [
       "Restart the laptop.",
       "Check for a touchpad on/off key (Fn plus a function key) or the setting in Settings > Bluetooth & devices > Touchpad.",
       "Connect an external USB keyboard or mouse to see whether the built-in hardware is the problem.",
       "If keys or the touchpad are damaged or liquid was spilled, power off and seek professional repair.",
   ])
_r("KM2", "input", {"km_builtin": "no", "km_wireless": "yes", "km_battery": "no"},
   "Weak batteries or device switched off", 50, "High", [
       "Replace the batteries or recharge the device.",
       "Turn on the power switch on the keyboard or mouse.",
       "Move the device closer to its receiver.",
   ])
_r("KM3", "input", {"km_builtin": "no", "km_wireless": "yes", "km_battery": "yes"},
   "Wireless pairing, receiver, or interference problem", 40, "Medium", [
       "Unplug the USB receiver and plug it into another port.",
       "For Bluetooth, remove the device and pair it again.",
       "Move away from interference such as metal surfaces and other wireless devices.",
       "Restart the computer.",
   ])
_r("KM4", "input", {"km_builtin": "no", "km_wireless": "no"},
   "Loose connection, faulty USB port, or faulty device", 40, "Medium", [
       "Unplug the device and plug it into a different USB port; avoid unpowered USB hubs.",
       "Check the cable for damage and try the device on another computer.",
       "In Device Manager, uninstall the device and restart; Windows reinstalls it automatically.",
       "Replace the device if it fails on other computers too.",
   ])

# ---------------------------------------------------------------- 9. APPLICATION NOT RESPONDING
_q("ap_wait", "app_hang", "Have you waited at least two minutes to see whether the application recovers on its own?")
_q("ap_one", "app_hang", "Does the problem happen only with this one application, while other programs work normally?")
_q("ap_always", "app_hang", "Does the application freeze every time you open or use it, not just occasionally?")

_r("AP1", "app_hang", {"ap_wait": "no"},
   "The application may still be busy", 60, "Medium", [
       "Wait two full minutes without clicking repeatedly; heavy tasks can make a program look frozen.",
       "Avoid force-closing too early, because you may lose unsaved work.",
       "If it is still frozen after two minutes, run this diagnosis again.",
   ])
_r("AP2", "app_hang", {"ap_wait": "yes", "ap_one": "no"},
   "System-wide resource shortage or system problem", 45, "Medium", [
       "Save your work if you can.",
       "Press Ctrl + Shift + Esc and check CPU, Memory, and Disk usage.",
       "Close other programs, then restart the computer.",
       "See the 'Computer is running slowly' category for more checks.",
   ])
_r("AP3", "app_hang", {"ap_wait": "yes", "ap_one": "yes", "ap_always": "yes"},
   "Damaged installation, bad update, or compatibility problem", 45, "Medium", [
       "Update the application to the latest version.",
       "Open Settings > Apps > Installed apps > the app > Advanced options > Repair, if available.",
       "Try running it in compatibility mode (right-click > Properties > Compatibility).",
       "Reinstall only after backing up your files and settings, because uninstalling can remove local data.",
   ])
_r("AP4", "app_hang", {"ap_wait": "yes", "ap_one": "yes", "ap_always": "no"},
   "Temporary glitch, very large file, or add-in/extension conflict", 30, "Low", [
       "Open Task Manager, select the app, and click End task. Unsaved work will be lost.",
       "Restart the app and try with a smaller file or fewer tabs and windows.",
       "Disable add-ins or browser extensions, then check for app updates.",
       "Restart the computer if it happens again.",
   ])

# ---------------------------------------------------------------- 10. PRINTER
_q("pr_power", "printer", "Is the printer switched on and showing no error light or message?")
_q("pr_paper", "printer", "Does the printer show a paper jam, no paper, or a low ink/toner warning?")
_q("pr_conn", "printer", "Is the printer connected (USB cable plugged in, or on the same Wi-Fi/network as your computer)?")
_q("pr_queue", "printer", "Are documents stuck in the print queue with a status of Pending or Error?")

_r("PR1", "printer", {"pr_power": "no"},
   "Printer is off, has no power, or is in an error state", 55, "High", [
       "Check the power cable and wall socket, then press the printer's power button.",
       "Read any message or light on the printer and look it up in the manual.",
       "Turn the printer off, wait 30 seconds, and turn it on again.",
       "If it will not turn on, do not open it; contact the manufacturer or a technician.",
   ])
_r("PR2", "printer", {"pr_power": "yes", "pr_paper": "yes"},
   "Paper jam, empty paper tray, or low ink/toner", 50, "High", [
       "Turn the printer off and unplug it.",
       "Gently remove jammed paper in the direction of the paper path, following the manual. Never force it.",
       "Refill the paper tray or replace empty cartridges.",
       "Do not touch hot internal parts of a laser printer; let them cool first.",
   ])
_r("PR3", "printer", {"pr_power": "yes", "pr_paper": "no", "pr_conn": "no"},
   "Printer is not connected to the computer or network", 45, "High", [
       "For USB, reconnect the cable firmly and try another USB port.",
       "For Wi-Fi, check the printer is connected to the same network as your computer.",
       "Restart the printer, the router, and the computer.",
       "Re-add the printer in Settings > Bluetooth & devices > Printers & scanners.",
   ])
_r("PR4", "printer", {"pr_power": "yes", "pr_paper": "no", "pr_conn": "yes", "pr_queue": "yes"},
   "Stuck print queue or printer shown as offline", 40, "Medium", [
       "Open Settings > Bluetooth & devices > Printers & scanners > your printer > Open print queue.",
       "Cancel all documents in the queue.",
       "If they will not clear, restart the Print Spooler service (Services > Print Spooler > Restart).",
       "If Windows shows the printer as 'Offline', restart the printer and try printing again.",
   ])
_r("PR5", "printer", {"pr_power": "yes", "pr_paper": "no", "pr_conn": "yes", "pr_queue": "no"},
   "Printer driver or settings problem", 30, "Low", [
       "Check your printer is selected as the default printer.",
       "Run the Windows printer troubleshooter.",
       "Download the latest driver from the printer manufacturer's website and reinstall it.",
       "Try printing a test page from the printer's Properties window.",
   ])


# ---------------------------------------------------------------- self-check
def validate_knowledge_base():
    """Return a list of problems found in the knowledge base (empty list = OK)."""
    problems = []
    category_ids = {c["id"] for c in CATEGORIES}
    seen_ids = set()
    for rule in RULES:
        if rule["id"] in seen_ids:
            problems.append("Duplicate rule id: " + rule["id"])
        seen_ids.add(rule["id"])
        if rule["category"] not in category_ids:
            problems.append(rule["id"] + ": unknown category " + rule["category"])
        for qid, value in rule["conditions"].items():
            if qid not in QUESTIONS:
                problems.append(rule["id"] + ": unknown question " + qid)
            elif QUESTIONS[qid]["category"] != rule["category"]:
                problems.append(rule["id"] + ": question " + qid + " is in another category")
            if value not in ("yes", "no"):
                problems.append(rule["id"] + ": condition value must be 'yes' or 'no'")
        if not rule["steps"]:
            problems.append(rule["id"] + ": has no steps")
    for cat in CATEGORIES:
        count = sum(1 for r in RULES if r["category"] == cat["id"])
        if count < 3:
            problems.append(cat["id"] + ": has fewer than 3 rules")
    if len(RULES) < 25:
        problems.append("Fewer than 25 rules in total")
    return problems


if __name__ == "__main__":
    issues = validate_knowledge_base()
    print("Categories:", len(CATEGORIES))
    print("Questions :", len(QUESTIONS))
    print("Rules     :", len(RULES))
    print("Problems  :", issues if issues else "none")
