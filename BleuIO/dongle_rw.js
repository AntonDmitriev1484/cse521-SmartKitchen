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

    // Added code: Wrapper functions around AT commands.

    const setCentralRole = () => {

        return writeData('AT+CENTRAL');

        // new Promise((resolve, reject) => {
        //     writeData('AT+CENTRAL')
        //         .then(() => {
        //             return readData(); // Return the inner promise
        //         })
        //         .then(() => {
        //             resolve(); // Resolve the outer promise if both writeData and readData are successful
        //         })
        //         .catch(err => {
        //             console.log(err);
        //             reject(err); // Reject the outer promise if there's any error
        //         });
        // });

    }

    const gapScan = () => {
        return writeData('AT+GAPSCAN');
        // new Promise( (resolve, reject) => {
        //     writeData('AT+GAPSCAN').then ( () => {
        //         resolve();
        //     })
        //     .catch ( (err) => {
        //         reject();
        //     })
        // })
    }

    return {
      writeData,
      readData,
      setCentralRole,
      gapScan
    };
  };
  