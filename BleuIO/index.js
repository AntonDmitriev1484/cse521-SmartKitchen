import { SerialPort } from "serialport"
// const { SerialPort } = require("serialport");

const bleuIO = (portPath) => {
    let readDataArray = [];
    const port = new SerialPort({
      path: portPath,
      baudRate: 115200,
      dataBits: 8,
      parity: "none",
      stopBits: 1,
    });
  
    const writeData = async (cmd) => {
      port.on("open", () => {
        port.write(cmd + "\r\n", (err) => {
          if (err) {
            return console.log("Error writing data: ", err.message);
          } else {
            return console.log(cmd + " command written");
          }
        });
      });
    };
  
    const readData = () => {
      return new Promise(function (resolve, reject) {
        port.on("readable", () => {
          let data = port.read();
          let enc = new TextDecoder();
          let arr = new Uint8Array(data);
          arr = enc.decode(arr);
        let removeRn = arr.replace(/\r?\n|\r/gm, "\n");
        if (removeRn != null) readDataArray.push(removeRn);
        //   readDataArray.push(arr);
          return resolve(readDataArray);
        });
      });
    };
  
    return {
      writeData,
      readData,
    };
  };
  
  

// const DEVICE_INSTANCE_PATH = 'USB\\VID_2DCF&PID_6002\\4048FDE85A27';

const DEVICE_INSTANCE_PATH = 'COM5';
// Sometimes you just need to run the node script through elevated (run as admin) command prompt?

try {
    const portUtils = bleuIO(DEVICE_INSTANCE_PATH);

    portUtils.writeData("ATI").then(() => {  // Write AT command along serial port that will request data from device
        
        setTimeout( () => {
            portUtils.readData().then((data) => {
            console.log("Data read from serial port:", data);
        })
        }
        , 3000);

        setTimeout( )

    }).catch((err) => {
        console.log(err);
    })

}
catch (err) {
    console.log(err);
}

function GapScan() {
    // Put dongle on central role
    // my_dongle.at_central().then(()=>{
    //enable rssi for the scan response
    // my_dongle.at_showrssi(1).then(()=>{
    //     //filter advertised data , so it only shows close beacon on the response
    //     my_dongle.at_findscandata('9636C6F7',6).then((data)=>{
    //       //convert array string to array of object with key value
}
