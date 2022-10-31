# READ ME

Disclaimer: I have no knowledge of programing or electronics, so this project is for learning and trying new stuff, probably has a lot of errors and bad practices. 

Project to use a servo to activate an old heating device on a specific date and time.

The idea is to use a Raspberry pi pico, RTC, servo s90, LCD 16x2, power source, level shifter and 3 buttons.

The user can select a date using the 3 buttons, the actual date is shown and the user can select a new date. The user input is stored in a txt file in the pico just in case there is a power outage or a soft reboot. The main program reads the date from the RTC and checks it from the date stored in the txt file, if the date is a match, the pico moves the servo to push the heater on/off button.

The main program uses 2 threads, the main thread runs the RTC and checks it against the user input, the second thread handles the information shown on the LCD. The buttons have a debounce timer function and are called by an IRQ.

--

The hardware is built using 2 lines of power from a power source that changes 220v into 5v and 3.3v, every component is connected to its respective power line and there is a level shifter to handle the 5v logic signals from the RTC, servo and LCD to the 3.3v of the pico. Probably it is not necessary in some of the devices, but all the hardware was salvaged from an Arduino kit, so it is designed for 5V and since I don't know better, the level shifter appears to be a safe choice.
