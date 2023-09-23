import { SerialPort } from "serialport";

// SOURCE: https://github.com/smart-sensor-devices-ab/bleuio-nodejs-library/blob/master/index.js

export default function init_bleuIO(portPath) {
    let readDataArray = [];
    const port = new SerialPort({
      path: portPath,
      baudRate: 115200,
      dataBits: 8,
      parity: "none",
      stopBits: 1,
    });
    //port.setMaxListeners(20);
  
    const writeData = async (cmd) => {
      console.log('starting '+cmd)

      port.on("open", () => {
        console.log('writing command: '+cmd);
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
      return new Promise(
        (resolve, reject) => {

          const listener = () => {
            let data = port.read();
            //port.removeListener('readable',listener);
            let enc = new TextDecoder();
            let arr = new Uint8Array(data);
            arr = enc.decode(arr);
            let removeRn = arr.replace(/\r?\n|\r/gm, "\n");
            if (removeRn != null) readDataArray.push(removeRn);
            return resolve(readDataArray);
          };

          port.on("readable", listener);
        }
        );
    }

        
      

    // Added code: Wrapper functions around AT commands.

    const setCentralRole = () => {
        return writeData('AT+CENTRAL');
    }

    const gapScan = (seconds) => {
        return writeData('AT+GAPSCAN+'+seconds);
    }

    return {
      writeData,
      readData,
      setCentralRole,
      gapScan
    };

  };
  