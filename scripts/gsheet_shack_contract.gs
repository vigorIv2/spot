/*
 * script to export data in first sheet in the current spreadsheet as a SHACk smart contract
 * author: Igor Vasilchikov
*/

function onOpen() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tokenizeMenuEntries = [{name: "Tokenize", functionName: "saveContracts"}];
  ss.addMenu("SHACk", tokenizeMenuEntries);
};

function folderByName(dapp,foldername){
  var folder = dapp.getFoldersByName(foldername);
  if(!folder.hasNext()){
    Logger.log("No Folder "+foldername+" Found");
    return null
  } else {
    Logger.log("Folder "+foldername+" Found")
    return folder.next();
  }
}

function fileByName(dapp,filename){
  var file = dapp.getFilesByName(filename);
  if(!file.hasNext()){
    Logger.log("No file "+filename+" Found");
    return null
  } else {
    Logger.log("File "+filename+" Found")
    return file.next();
  }
}

function saveContracts() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var folder=folderByName(DriveApp,"SHACk");
  var contractFolder=null;
  if ( folder != null ) { 
    contractFolder=folderByName(folder,"SmartContract");
    folder=folderByName(folder,"PropertiesDocuments");
  }
  var cfAll=contractFolder.getFilesByName("shack_smart_contract.sol");
  var cf = null;
  var template = null;
  var templateLines = null;
  if ( cfAll.hasNext() ) {
    cf = cfAll.next();
    template = cf.getAs("application/octet-stream");
    templateLines = template.getDataAsString().split("\n");
    Logger.log("TemplateLines.length="+templateLines.length);
  } else {
    Browser.msgBox("Template for SHACk Smart Contract is missing, \nfix that and run again!");
    return
  }
  var sheet = sheets[0];
  var activeRange = sheet.getDataRange();
  var data = activeRange.getValues();
  var genCnt = 0;
  for (var r = 0 ; r < data.length ; r++) {
    var tokenId = data[r][14].toString().replace(/[\ _\.]*$/, "" );
    if ( tokenId.indexOf("SHK.") == 0 ) { // for non empty data rows only 
      var subfolder = folderByName(folder,tokenId);
      if ( subfolder == null ) { // subfolder did not exist, create it and populate 
        subfolder = folder.createFolder(tokenId);
        Logger.log("Subfolder "+subfolder.getName()+" created");
      } else {
        Logger.log("Subfolder "+subfolder.getName()+" already exist");
      }
      var fileName = "contract_"+tokenId+ ".sol";
      var file = fileByName(subfolder,fileName);
      if ( file == null ) {
        var rate = data[r][7].toString().replace(/\.[\d]*/, "" );
        var fundAcc = data[r][10];
        var tokenAcc = data[r][11];
        var term = data[r][13];
        var tokenCap = data[r][15].toString().replace(/\.[\d]*/, "" );
        var tokenGoal = data[r][16].toString().replace(/\.[\d]*/, "" );
        Logger.log("TokenId="+tokenId+" rate="+rate+" fundAcc="+fundAcc+" tokenAcc="+tokenAcc+" tokenCap="+tokenCap+" tokenGoal="+tokenGoal);
        var contractSrc = "";
        for (var l = 0; l <= templateLines.length; l++) {
          var tl = templateLines[l];
          if ( tl == null ) {
            break;
          }
          
          var nl = tl;
          // substitute Smart contract custom parameters
          nl=nl.replace(/\_rate\ =\ [\d]*.*;/, "_rate = "+rate+"; // upd "  );
          nl=nl.replace(/\_wallet\ *=\ *.*;/, "_wallet = "+fundAcc+"; // upd " );
          nl=nl.replace(/remainingWallet\ *=\ *.*;/, "remainingWallet = "+tokenAcc+"; // upd " );
          nl=nl.replace(/crowdsaleTokenName\ *=\ \"*.*\";/, "crowdsaleTokenName = \""+tokenId+" ("+term+"m)\"; // upd " );
          nl=nl.replace(/crowdsaleTokenSymbol\ *=\ \"*.*\";/, "crowdsaleTokenSymbol = \""+tokenId+"\"; // upd " );
          nl=nl.replace(/TOKENS\_CAP\ *=\ *[\d]*.*;/, "TOKENS_CAP = "+tokenCap+"; // upd " );
          nl=nl.replace(/tokensGoal\ *=\ *[\d]*.*;/, "tokensGoal = "+tokenGoal+"; // upd " );
          contractSrc += nl + "\n";
        }
        Logger.log("Generating Smart Contract "+fileName) ;
        subfolder.createFile(fileName, contractSrc);
        Logger.log("Generated Smart Contract "+fileName) ;
        genCnt++;
      } else {
        Logger.log("Smart Contract "+fileName+" already exist");        
      }
    }
  }
  if ( genCnt > 0 ) {
    Browser.msgBox( genCnt+' Contracts were generated in ' + folder.getName());
  } else {
    Browser.msgBox( 'No contracts were generated in ' + folder.getName());
  }
}


