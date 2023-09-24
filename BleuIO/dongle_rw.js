import { SerialPort } from "serialport";

// SOURCE: https://github.com/smart-sensor-devices-ab/bleuio-nodejs-library/blob/master/index.js

export default function init_bleuIO(portPath) {
    let readDataArray = [];

    let MAP_ADDR_TO_RSSI = {};

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

    const bindToOnRead = (onReadFunction) => {
      // At the moment, the only readables are the gapscan results
      port.on("readable", () => {
        let data = port.read(); 
        let enc = new TextDecoder();
        let info = new Uint8Array(data);
        info = enc.decode(info);
        console.log(info);
        info = JSON.parse(info);

        let scan = info;
        MAP_ADDR_TO_RSSI[scan.addr] = scan.rssi;
        // Update our map with this information
      });
    }

    //Maybe just constantly have this loop. So we get a full stream of responses from the device?

    // Added code: Wrapper functions around AT commands.

    const setCentralRole = () => {

        return writeData('AT+CENTRAL');

    }

    const gapScan = () => {
        return writeData('AT+GAPSCAN');

    }

    const getRSSI = (addr) => {
      return MAP_ADDR_TO_RSSI[addr];
    }

    return {
      writeData,
      readData,
      setCentralRole,
      gapScan,
      bindToOnRead
    };
  };
  