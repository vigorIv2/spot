package com.huhula.credentials;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.web3j.crypto.WalletUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import joptsimple.OptionParser;
import joptsimple.OptionSet;
import sun.rmi.runtime.Log;


import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;

public class Wallets {

    private java.io.File tempDir ;
    private static final Logger LOG = LoggerFactory.getLogger(Wallets.class);
    private Config defaultConfig ;
    private Connection huhulaDbConn;
    private Connection walletDbConn;

    public Wallets(String configFileName) {
        defaultConfig = ConfigFactory.parseFile(new File(configFileName));

        LOG.info("db addr = "+defaultConfig.getString("conf.cocroachaddress"));
        LOG.info("db user = "+defaultConfig.getString("conf.huhuladbuser"));
        tempDir = new File(defaultConfig.getString("conf.tempDir"));

    }

    public void connectDb() {
        try {
            Class.forName("org.postgresql.Driver");
            String dbAddr = defaultConfig.getString("conf.cocroachaddress");
            String dbPort = defaultConfig.getString("conf.cocroachport");
            String dbName = defaultConfig.getString("conf.huhuladb");
            String dbUser = defaultConfig.getString("conf.huhuladbuser");
            String dbPwd = defaultConfig.getString("conf.huhuladbpwd");
            huhulaDbConn = DriverManager.getConnection("jdbc:postgresql://" + dbAddr + ":" + dbPort + "/" + dbName + "?user=" + dbUser + "&sslcert=/Users/ivasilchikov/spot/certs/client.huhulaman.der&sslkey=/Users/ivasilchikov/spot/certs/client.huhulaman.key.pk8&sslmode=require&ssl=true", dbUser, dbPwd);
        } catch ( Throwable ce ) {
            LOG.error("Error on attempt to connect to db",ce);
        }
    }

    public void readDb() throws java.sql.SQLException {
        try {
            // Create the "accounts" table.
            ResultSet res = huhulaDbConn.createStatement().executeQuery("SELECT * FROM users");
            while (res.next()) {
                System.out.printf("\taccount %s: %s\n", res.getString("id"), res.getString("userhash"));
            }
        } finally {
            // Close the database connection.
            huhulaDbConn.close();
        }
    }

    public String get_SHA_512_SecurePassword(String passwordToHash, String salt){
        String generatedPassword = null;
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-512");
            md.update(salt.getBytes(StandardCharsets.UTF_8));
            byte[] bytes = md.digest(passwordToHash.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for(int i=0; i< bytes.length ;i++){
                sb.append(Integer.toString((bytes[i] & 0xff) + 0x100, 16).substring(1));
            }
            generatedPassword = sb.toString();
        }
        catch (NoSuchAlgorithmException e){
            e.printStackTrace();
        }
        return generatedPassword;
    }

    public String generateWallet(String password) {
        String content = "";
        String fileName = "";
        try {
            fileName = WalletUtils.generateFullNewWalletFile(password, tempDir);
            content = new String(Files.readAllBytes(Paths.get(tempDir+"/"+fileName)));
        } catch (Throwable t) {
            LOG.error("Error while creating wallet file",t);
        } finally {
            if ( ! fileName.isEmpty() ) {
                try {
                    Files.delete(Paths.get(tempDir+"/"+fileName));
                } catch ( Throwable et ) {
                    LOG.error("Error on attempt to delete file "+tempDir+"/"+fileName);
                }
            }
        }
        return content;
    }

    public static void main(String [] args) {
        OptionParser parser = new OptionParser( "wc:" );
        parser.accepts("c").withRequiredArg();


        OptionSet options = parser.parse( args );
        assert( options.has("c") );
        assert( options.hasArgument("c") );
        String configName = options.valueOf("c").toString();
        Wallets ws = new Wallets(configName);


        if ( options.has("w") ) { // create wallets
            // just some temp code for now
            String pwd = ws.get_SHA_512_SecurePassword("0414cae0-0492-4e2e-bd58-230938eb06a9", "110865176290720544754");
            String keyFileName = ws.generateWallet(pwd);


            LOG.info("Wallet file content " + keyFileName);
            LOG.info("Wallet pwd " + pwd);

            ws.connectDb();
            try {
                ws.readDb();
            } catch (SQLException se) {
                LOG.error("SQLException ", se);
            }
        }
    }
}
