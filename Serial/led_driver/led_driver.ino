
const int NUM_LEDS = 144;
unsigned int pixels[NUM_LEDS];
byte last_cmd = 255;

byte mode = 1;
int ptr = 0;

void setup() {

  Serial.begin(115200);
}

void loop() {

  // Listen for the next command
  last_cmd = read_command();

  // Processes the command
  process_command();

  // Send a handshake back to Master
  for (int i =0; i< NUM_LEDS; i++)
  {
    Serial.print(pixels[i]);
    Serial.print(",");
  }
    
  Serial.print((char) 254);
}

void wait_for_data()
{
  while(Serial.available() == 0);
}

int read_command()
{
  /***
   * This function reads in a command over Serial.
   * The command 'm' signifies a mode switch, either mode 1 or 2.
   * The command 'd' signifies incomming data for the current mode
   */
  // Wait for incoming command
  wait_for_data();

  // Read the command and store it
  return Serial.read();
  
}

void fill_mode_1()
{
  /***
   * This function fills the pixel array with a single value
   */
   wait_for_data();
   byte value = Serial.read();

   for (int i = 0; i < NUM_LEDS; i++)
   {
      pixels[i] = value;
   }
}

void fill_mode_2()
{
  /***
   * This function fills the pixel array with an individual value at each index
   */
   for (int i =0; i < NUM_LEDS; i++)
   {
    wait_for_data();
    pixels[i] = Serial.read();
   }
}


int process_command()
{
  // Switch mode, expects a single byte
  if (last_cmd == (int) 'm')
  {

    wait_for_data();
    
    mode = Serial.read(); // Store the new mode
  }
  // Store data. If mode is 1, expects a single value for all pixels.
  // If mode is 2, expects an individual value for all pixels
  else if (last_cmd == (int) 'd')
  {

    if (mode == 1)
    {
      fill_mode_1();
    }
    else if (mode == 2)
    {
      fill_mode_2();
    }
    
  }
  
}

