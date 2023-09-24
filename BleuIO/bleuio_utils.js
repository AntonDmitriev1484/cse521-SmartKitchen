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

    // const openPort = async () => {
    //   port.open((error) => {
    //     if (error) {
    //       console.error('Error opening port:', error);
    //     } else {
    //       console.log(`Port ${portPath} is open.`);
    //       // Perform communication with the port here
    //     }
    //   });
    // }

    port.on('open', () => console.log('Port open'));
  
    const writeData = async (cmd) => {
        port.write(cmd + "\r\n", (err) => {
          if (err) {
            return console.log("Error writing data: ", err.message);
          } else {
            return console.log(cmd + " command written");
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
        catch (err) {}
      });
    }

    // AT Commands: https://www.bleuio.com/getting_started/docs/commands/

    const setCentralRole = () => {
        return writeData('AT+CENTRAL');
    }

    const gapScan = (interval) => {
      // Does each gapscan only detect devices it previously hasn't?
      // Need to figure out some way to clear that tracker.

        return writeData('AT+GAPSCAN='+interval);
        //return writeData('AT+GAPSCAN');
    }

    return {
      writeData,
      setCentralRole,
      gapScan,
      onReadableEvent,
    };
  };
  

  // Ok as illustrated by the Serial terminal
  // It re-scans everything with each gapscan

  /*
  AT+GAPSCAN
{"C":2,"cmd":"AT+GAPSCAN"}
{"A":2,"err":0,"errMsg":"ok"}
{"R":2,"evt":{"action":"scanning"}}
{"E":2,"nol":4}
{"S":2,"rssi":-37,"addr":"[1]22:C6:AF:F2:6A:06"}
{"S":2,"rssi":-62,"addr":"[0]24:FC:E5:77:F0:35"}
{"S":2,"rssi":-80,"addr":"[1]3D:2E:BF:77:92:4C"}
{"S":2,"rssi":-77,"addr":"[1]59:0C:04:4B:EF:C0"}
{"S":2,"rssi":-39,"addr":"[1]58:23:57:28:6A:43"}
{"S":2,"rssi":-84,"addr":"[1]65:9D:F7:EA:46:B4"}
{"S":2,"rssi":-87,"addr":"[1]EB:B8:F5:DE:1B:20","name":"NORA_BED"}
{"S":2,"rssi":-83,"addr":"[1]47:77:47:F6:14:F9"}
{"S":2,"rssi":-86,"addr":"[1]79:DF:B8:58:A2:AC"}
{"S":2,"rssi":-90,"addr":"[0]D0:03:DF:61:8F:10"}
{"S":2,"rssi":-84,"addr":"[1]6E:57:5E:62:30:78"}
{"S":2,"rssi":-70,"addr":"[0]5C:F9:38:D1:C3:A3"}
{"S":2,"rssi":-85,"addr":"[1]C8:73:3B:2B:E2:72"}
{"S":2,"rssi":-83,"addr":"[1]CE:CA:DB:AC:55:D9"}
{"S":2,"rssi":-91,"addr":"[1]52:EF:94:27:4E:69"}
{"S":2,"rssi":-94,"addr":"[1]5C:D9:D9:06:36:3F"}
{"S":2,"rssi":-87,"addr":"[1]ED:FB:1E:D4:2A:C9"}
{"S":2,"rssi":-94,"addr":"[0]16:CB:19:DE:AB:22"}
{"S":2,"rssi":-90,"addr":"[1]4A:21:C6:34:02:44"}
{"S":2,"rssi":-79,"addr":"[1]E3:20:41:2C:03:5E"}
{"S":2,"rssi":-88,"addr":"[1]6F:D9:52:BD:96:AF"}
{"S":2,"rssi":-90,"addr":"[0]40:22:D8:26:81:D6"}
{"S":2,"rssi":-88,"addr":"[1]C3:F9:9D:49:34:A0"}
{"S":2,"rssi":-84,"addr":"[1]C6:6B:AF:EF:5A:A3"}
{"S":2,"rssi":-95,"addr":"[1]14:22:98:3A:22:F8"}
{"S":2,"rssi":-89,"addr":"[1]FA:1C:50:6E:66:9D"}
{"S":2,"rssi":-91,"addr":"[1]15:C5:E4:1D:63:F6"}

{"SE":2,"evt":{"action":"scan completed"}}
AT+GAPSCAN
{"C":3,"cmd":"AT+GAPSCAN"}
{"A":3,"err":0,"errMsg":"ok"}
{"R":3,"evt":{"action":"scanning"}}
{"E":3,"nol":4}
{"S":3,"rssi":-79,"addr":"[1]59:0C:04:4B:EF:C0"}
{"S":3,"rssi":-79,"addr":"[1]47:77:47:F6:14:F9"}
{"S":3,"rssi":-42,"addr":"[1]58:23:57:28:6A:43"}
{"S":3,"rssi":-68,"addr":"[0]5C:F9:38:D1:C3:A3"}
{"S":3,"rssi":-37,"addr":"[1]22:C6:AF:F2:6A:06"}
{"S":3,"rssi":-83,"addr":"[1]3D:2E:BF:77:92:4C"}
{"S":3,"rssi":-65,"addr":"[0]24:FC:E5:77:F0:35"}
{"S":3,"rssi":-86,"addr":"[0]D0:03:DF:61:8F:10"}
{"S":3,"rssi":-74,"addr":"[1]6E:57:5E:62:30:78"}
{"S":3,"rssi":-86,"addr":"[1]79:DF:B8:58:A2:AC"}
{"S":3,"rssi":-89,"addr":"[1]65:9D:F7:EA:46:B4"}
{"S":3,"rssi":-81,"addr":"[1]E3:20:41:2C:03:5E"}
{"S":3,"rssi":-90,"addr":"[0]40:22:D8:26:81:D6"}
{"S":3,"rssi":-93,"addr":"[1]FA:1C:50:6E:66:9D"}
{"S":3,"rssi":-92,"addr":"[0]40:22:D8:26:81:D6","name":"Core200S"}
{"S":3,"rssi":-86,"addr":"[1]C8:73:3B:2B:E2:72"}
{"S":3,"rssi":-74,"addr":"[1]CE:CA:DB:AC:55:D9"}
{"S":3,"rssi":-89,"addr":"[1]6F:D9:52:BD:96:AF"}
{"S":3,"rssi":-91,"addr":"[1]52:EF:94:27:4E:69"}
{"S":3,"rssi":-84,"addr":"[1]C6:6B:AF:EF:5A:A3"}
{"S":3,"rssi":-92,"addr":"[1]4A:21:C6:34:02:44"}
{"S":3,"rssi":-88,"addr":"[1]EB:B8:F5:DE:1B:20","name":"NORA_BED"}
{"S":3,"rssi":-86,"addr":"[1]ED:FB:1E:D4:2A:C9"}
{"S":3,"rssi":-91,"addr":"[0]16:CB:19:DE:AB:22"}

{"SE":3,"evt":{"action":"scan completed"}}
*/