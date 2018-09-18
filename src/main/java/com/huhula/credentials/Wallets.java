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


import java.io.File;
import java.sql.*;

public class Wallets {

    private java.io.File tempDir ;
    private static final Logger LOG = LoggerFactory.getLogger(Wallets.class);
    private Config defaultConfig ;
    private String rootDir;

    public Wallets(String _configFileName,String _rootDir) {
        rootDir = _rootDir;
        defaultConfig = ConfigFactory.parseFile(new File(_configFileName));
        tempDir = new File(defaultConfig.getString("conf.tempDir"));
    }

    public Connection connectDb(String dbSection) {
        try {
            Class.forName("org.postgresql.Driver");
            String dbAddr = defaultConfig.getString("conf."+dbSection+".dbaddress");
            String dbPort = defaultConfig.getString("conf."+dbSection+".dbport");
            String dbName = defaultConfig.getString("conf."+dbSection+".dbname");
            String dbUser = defaultConfig.getString("conf."+dbSection+".dbuser");
            String dbPwd = defaultConfig.getString("conf."+dbSection+".dbpassword");

            String jdbcUrl = "jdbc:postgresql://" + dbAddr + ":" + dbPort + "/" + dbName + "?user=" + dbUser + "&sslcert="+rootDir+"/certs/client."+dbUser+".der&sslkey="+rootDir+"/certs/client."+dbUser+".key.pk8&sslmode=require&ssl=true";
            LOG.info("Connecting to "+jdbcUrl);
            Connection aConn = DriverManager.getConnection(jdbcUrl, dbUser, dbPwd);
            aConn.setAutoCommit(false);
            return aConn;
        } catch ( Throwable ce ) {
            LOG.error("Error on attempt to connect to db ",ce);
        }
        return null;
    }

    public String saveWallet(Connection walletsDbConn, String json) {
        String uuid = null;
        try {
            LOG.info("Beginning to saveWallet");
            PreparedStatement ps = walletsDbConn.prepareStatement("insert into ethereum(utc_json) values(?)", Statement.RETURN_GENERATED_KEYS);
            ps.setString(1,json);
            ps.executeUpdate();
            ResultSet rs = ps.getGeneratedKeys();
            if(rs != null && rs.next()){
                uuid=rs.getString(1);
                LOG.info("Generated row id "+uuid);
            }
            rs.close();
            ps.close();
            walletsDbConn.commit();
        } catch ( SQLException se ) {
            LOG.error("SQLException in saveWallet", se);
        }
        return uuid;
    }

    public void provisionWallets() {
        Connection huhulaDbConn = null;
        Connection walletsDbConn = null;
        PreparedStatement ps = null;
        PreparedStatement ups = null;
        try {
            try {
                LOG.info("Beginning to provision new wallets");
                huhulaDbConn = connectDb("huhula");
                walletsDbConn = connectDb("wallets");
                ps = walletsDbConn.prepareStatement("insert into ethereum(utc_json) values(?)", Statement.RETURN_GENERATED_KEYS);
                ups = huhulaDbConn.prepareStatement("update users set wid = ? where id = ?");

                ResultSet res = huhulaDbConn.createStatement().executeQuery("SELECT id, userhash FROM users where wid is null;");
                while (res.next()) {
                    String uid = res.getString("id");
                    String uhash = res.getString("userhash");
                    LOG.info("Provisioning wallet for user ID="+uid+"+"+uhash);

                    String pwd = get_SHA_1_SecurePassword(uid, uhash);
                    String keyFile = generateWallet(pwd);
                    LOG.info("Wallet file generated key Length = "+keyFile.length());

                    // save to db
                    ps.setString(1,keyFile);
                    ps.executeUpdate();
                    ResultSet rs = ps.getGeneratedKeys();
                    if(rs != null && rs.next()) { // get the id of generated row and insert it to users as fk
                        String wid=rs.getString(1);
                        LOG.info("Generated wallet row id "+wid);
                        try {
                            ups.setString(1, wid);
                            ups.setString(2, uid);
                            ups.executeUpdate();
                            walletsDbConn.commit();
                            huhulaDbConn.commit();
                            LOG.info("Updated user id "+uid+" with wid "+wid);
                        } catch ( SQLException sqe ) {
                            LOG.error("SQLException while updating huhula or wallets",sqe);
                            huhulaDbConn.rollback();
                            walletsDbConn.rollback();
                        }
                    }
                    rs.close();
                }
                res.close();
            } finally {
                LOG.info("Done provisioning new wallets");
                if ( ps != null )
                    ps.close();
                if ( ups != null )
                    ups.close();
                if ( huhulaDbConn != null )
                    huhulaDbConn.close();
                if ( walletsDbConn != null )
                    walletsDbConn.close();
            }
        } catch ( SQLException se ) {
            LOG.error("SQLException in provisionWallets", se);
        }
    }

    public String deprecated_get_SHA_512_SecurePassword(String passwordToHash, String salt){
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

    public String get_SHA_1_SecurePassword(String passwordToHash, String salt){
        String generatedPassword = null;
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
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
            LOG.info("File " + tempDir + "/" + fileName + " password=" + password);
        } catch (Throwable t) {
            LOG.error("Error while creating wallet file",t);
//        } finally {
//            if ( ! fileName.isEmpty() ) {
//                try {
//                    Files.delete(Paths.get(tempDir+"/"+fileName));
//                } catch ( Throwable et ) {
//                    LOG.error("Error on attempt to delete file "+tempDir+"/"+fileName);
//                }
//            }
        }
        return content;
    }

    public static void main(String [] args) {
        OptionParser parser = new OptionParser( "wc:r:p:" );
        parser.accepts("c").withRequiredArg();
        parser.accepts("r").withRequiredArg();
        parser.accepts("p").withRequiredArg();

        OptionSet options = parser.parse( args );
        assert( options.has("c") );
        assert( options.hasArgument("c") );
        assert( options.has("r") );
        assert( options.hasArgument("r") );
        String configName = options.valueOf("c").toString();
        String rootDir = options.valueOf("r").toString();
        Wallets ws = new Wallets(configName,rootDir);

        if ( options.has("w") ) { // create wallets
            ws.provisionWallets();
        } else
        if ( options.has("p") ) { // create wallets
            String uid = options.valueOf("p").toString().split("\\+")[0];
            String userhash = options.valueOf("p").toString().split("\\+")[1];
            LOG.info("Recovering password for uid="+uid+" uhash="+userhash);
            String pwd = ws.get_SHA_1_SecurePassword(uid, userhash);
            System.out.println(pwd);
        }
    }
}
