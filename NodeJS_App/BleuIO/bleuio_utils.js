import { SerialPort } from "serialport";

// SOURCE: https://github.com/smart-sensor-devices-ab/bleuio-nodejs-library/blob/master/index.js
// Ok the person who wrote this package did not know what they were doing ngl

export default function init_bleuIO(portPath) {
    const port = new SerialPort({
      path: portPath,
      baudRate: 115200,
      dataBits: 8,
      parity: "none",
      stopBits: 1,
    });

    port.on('open', () => {
      
      console.log('Port open')
        port.get((err, info) => {
          if (err) {
            console.error('Error getting device information:', err.message);
          } else {
            console.log('Device information:', info);
          }
        }
        )
    }
    );
  
    const writeData = async (cmd) => {
        port.write(cmd + "\r\n", (err) => {
          if (err) {
            return console.log("Error writing data: ", err.message);
          } else {
            //return console.log(cmd + " command written");
            return;
          }
        });
    };

    const onReadableEvent = (onReadFunction) => {
      // At the moment, the only readables are the gapscan results
      port.on("readable", () => {
        let data = port.read(); 
        let enc = new TextDecoder();
        let info = new Uint8Array(data);
        info = enc.decode(info);
        //console.log(info);
        try {
          info = JSON.parse(info);
          let scan = info;
          onReadFunction(scan);
        }
        catch (err) {
          // Sometimes errors in the try will keep anything from working
          // COMMENTING THIS OUT FOR NOW
          // console.log(err)
        }
      });
    }

    // AT Commands: https://www.bleuio.com/getting_started/docs/commands/

    const setCentralRole = () => {
        return writeData('AT+CENTRAL');
    }

    const gapScan = (interval) => {
        return writeData('AT+GAPSCAN='+interval);
    }

    return {
      writeData,
      setCentralRole,
      gapScan,
      onReadableEvent,
    };
  };