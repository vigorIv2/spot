package com.huhula.credentials;

import com.huhula.contract.ContractInteractions;
import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import joptsimple.OptionParser;
import joptsimple.OptionSet;
import org.json.JSONException;
import org.json.JSONObject;

import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.response.EthAccounts;
import org.web3j.protocol.core.methods.request.EthFilter;


import javax.sql.rowset.serial.SerialBlob;
import java.sql.*;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

public class Wallets {

    private java.io.File tempDir ;
    private static final Logger LOG = LoggerFactory.getLogger(Wallets.class);
    private String rootDir;
    private Settings conf;

    public Wallets(String _configPath,String _rootDir, String _chain) {
        rootDir = _rootDir;
        conf = new Settings(_configPath,_chain);
        tempDir = new File(conf.getString("tempDir"));
    }

    public Connection connectDb(String dbSection) {
        try {
            Class.forName("org.postgresql.Driver");
            String dbAddr = conf.getString(dbSection+".dbaddress");
            String dbPort = conf.getString(dbSection+".dbport");
            String dbName = conf.getString(dbSection+".dbname");
            String dbUser = conf.getString(dbSection+".dbuser");
            String dbPwd  = conf.getString(dbSection+".dbpassword");

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

    /**
     * returns array of two elements - file name, file content
     * @param walletscon - wallets db connection
     * @param wid - pk of the record
     * @return
     */
    public String[] fetchWallet(Connection walletscon, String wid) {
        PreparedStatement ps = null;
        List<String> wallet = new ArrayList<String>();

        try {
            LOG.debug("Beginning to load wallet for wid="+wid);
            ps = walletscon.prepareStatement("select utc_filename, utc_json FROM ethereum where id = ?;");
            ps.setString(1, wid);

            ResultSet res = ps.executeQuery();
            if (res.next()) {
                String fn = res.getString(1);
                String fc = res.getString(2);
                wallet.add(fn);
                wallet.add(fc);
                LOG.info("fetched wallet fn="+fn+" length:"+fc.length());
            } else {
                res.close();
                ps.close();
                throw new SQLDataException("Huhula integrity error, select returns no records");
            }
            res.close();
            ps.close();
        } catch ( SQLException se ) {
            LOG.error("SQLException in fetchWallet", se);
        }
        return wallet.toArray(new String[wallet.size()]);
    }

    public void saveWalletFile(String utcfname, String utccontent) {
        try {
            LOG.debug("Beginning to save wallet file to temp file "+utcfname);
            try (PrintWriter out = new PrintWriter(utcfname)) {
                out.println(utccontent);
            }
        } catch ( FileNotFoundException fne ) {
            LOG.error("FileNotFoundException while saving utc file "+utcfname,fne);
        }
    }

    public void payOff(String huhulaPwd) {

        Connection huhulaDbConn = null;
        Connection walletsDbConn = null;
        PreparedStatement psuserupdate = null;
        PreparedStatement psbillupdate = null;
        Credentials huhulacreds = null;
        int transactionsCount = 0;
        ContractInteractions ci = new ContractInteractions(conf);
        if ( ! ci.isHealthy() ) {
            LOG.error("ContractInteractions class is not healthy, giving up");
            return;
        } else {
            huhulacreds = ci.loadCredentials(huhulaPwd, conf.getUtcFile());
        }
        if ( huhulacreds == null ) {
            LOG.error("Credentials are empty, exiting");
            return;
        }
        BigInteger coinbasebalance = ci.getBalance(huhulacreds.getAddress());
        BigInteger e2 = BigDecimal.valueOf(2e18).toBigInteger();
        LOG.info("Huhula Coinbase balance "+coinbasebalance+ " comparing to "+e2);
        if ( coinbasebalance.compareTo(e2) < 0 ) {
            LOG.error("Coinbase balance is insufficient, refill wallet otherwise it won't be enough to pay for gas, exiting now");
            ci.shutdown();
            return;
        }
        BigInteger tokbal = ci.getTokenBalance(huhulacreds.getAddress());
        if ( tokbal.compareTo(BigDecimal.valueOf(1000e6).toBigInteger()) < 0 ) {
            LOG.error("Token balance is too low, refill wallet otherwise it won't be enough to pay for gas, exiting now");
            ci.shutdown();
            return;
        }

        try {
            SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
            String yts = format.format(new Date(System.currentTimeMillis()-86400000));
            LOG.info("Beginning to pay off balances of tokens today="+yts);
            huhulaDbConn = connectDb("huhula");
            walletsDbConn = connectDb("wallets");

            // select bill records that were no propagated to blockchain
            String selectBillSql = "select bp.user_id, bp.for_date, u.userhash, u.wid, bp.balance, u.account " +
                    "from bill_payable bp join users u on (bp.user_id = u.id) " +
                    "where not u.wid is null and bp.for_date < '"+yts+"' " +
                    "order by bp.user_id, bp.for_date";
            LOG.debug("SQL "+selectBillSql);
            psuserupdate = huhulaDbConn.prepareStatement("update users set chain_date = now(), balance = ? where id = ?;");
            psbillupdate = huhulaDbConn.prepareStatement("update bill set chain_date = now() where user_id = ? and for_date = ?;");

            ResultSet res = huhulaDbConn.createStatement().executeQuery(selectBillSql);
            while (res.next()) {
                String uid = res.getString(1);
                Date fordate = res.getDate(2);
                String userhash = res.getString(3);
                String wid = res.getString(4);
                Double balance = res.getDouble(5);
                String uacct = res.getString(6);

                psuserupdate.setDouble(1, balance);
                psuserupdate.setString(2, uid);

                psbillupdate.setString(1,uid);
                psbillupdate.setDate(2,fordate);

                LOG.info("Paying off balance of "+balance+" for user uid:"+uid+" date "+fordate);
                if (balance > 0) {
                    ci.depositToUser(balance, "0x"+uacct, huhulacreds);
                } else if (balance < 0) {
//                    String[] wallet = fetchWallet(walletsDbConn, wid);
//                    String ffn = conf.getTempDir() + File.separator + wallet[0];
//                    saveWalletFile(ffn, wallet[1]);
//                    String pwd = get_SHA_1_SecurePassword(uid, userhash);
//                    Credentials creds = ci.loadCredentials(pwd, ffn);
//                    ci.withdrawalFromUser(Math.abs(balance), conf.getPool(), creds);
                } else { // balance = 0
                    LOG.info("Balance equals to zero, nothing to update");
                }
                try {
                    int rcu = psuserupdate.executeUpdate();
                    assert(rcu == 1);
                    int rcub = psbillupdate.executeUpdate();
                    assert(rcub == 1);
                    huhulaDbConn.commit();
                    walletsDbConn.commit();
                } catch (SQLException ue) {
                    LOG.error("SQLException on update uid:" + uid, ue);
                    huhulaDbConn.rollback();
                    walletsDbConn.rollback();
                }
            }
            res.close();
            psuserupdate.close();
            LOG.info("Finished to pay off balances of tokens");
        } catch (SQLException se) {
            LOG.error("SQLException in provisionWallets", se);
        }
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
                ps = walletsDbConn.prepareStatement("insert into ethereum(utc_json,utc_filename) values(?,?);", Statement.RETURN_GENERATED_KEYS);
                ups = huhulaDbConn.prepareStatement("update users set wid = ?, account = ? where id = ?;");

                ResultSet res = huhulaDbConn.createStatement().executeQuery("SELECT id, userhash FROM users where wid is null;");
                while (res.next()) {
                    String uid = res.getString("id");
                    String uhash = res.getString("userhash");
                    LOG.info("Provisioning wallet for user ID="+uid+"+"+uhash);

                    String pwd = get_SHA_1_SecurePassword(uid, uhash);
                    String[] keyInfo = generateWallet(pwd);
                    LOG.info("Wallet file generated key Length = "+keyInfo[0].length());

                    // save to db
                    String[] kp = keyInfo[1].split(File.separator);
                    String utc_fn= kp[kp.length-1];
                    JSONObject utc = new JSONObject(keyInfo[0]);
                    String acct = utc.getString("address");
                    LOG.info("UTC File name:"+utc_fn+" account:"+acct);
                    LOG.debug("UTC File content :"+keyInfo[0]);
                    ps.setString(1,keyInfo[0]);
                    ps.setString(2,utc_fn);
                    ps.executeUpdate();
                    ResultSet rs = ps.getGeneratedKeys();
                    if(rs != null && rs.next()) { // get the id of generated row and insert it to users as fk
                        String wid=rs.getString(1);
                        LOG.info("Generated wallet row id "+wid);
                        try {
                            ups.setString(1, wid);
                            ups.setString(2, acct);
                            ups.setString(3, uid);
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

    public String[] generateWallet(String password) {
        String content = "";
        String fileName = "";
        try {
            fileName = WalletUtils.generateFullNewWalletFile(password, tempDir);
            content = new String(Files.readAllBytes(Paths.get(tempDir+"/"+fileName)));
            LOG.debug("File " + tempDir + "/" + fileName + " password=" + password);
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
        return new String[]{content,fileName};
    }

    public static void main(String [] args) {
        OptionParser parser = new OptionParser( "wc:r:p:e:b:" );
        parser.accepts("c").withRequiredArg();
        parser.accepts("r").withRequiredArg();
        parser.accepts("p").withRequiredArg();
        parser.accepts("e").withRequiredArg();
        parser.accepts("b").withRequiredArg();

        OptionSet options = parser.parse( args );

        if ( ! options.has("c") || ! options.has("r") ) {
            System.out.println("Usage: Huhula -<wc:p:r:e:>");
            System.out.println("   -c <config path>");
            System.out.println("   -w to create wallets");
            System.out.println("   -r <root dir>");
            System.out.println("   -p <recover password from uid>");
            System.out.println("   -b <huhula pwd>");
            System.out.println("   -e <blockchain environment such as rinkeby | main | ganache>");
            System.exit(1);
        }

        assert( options.has("c") );
        assert( options.hasArgument("c") );
        assert( options.has("r") );
        assert( options.hasArgument("r") );
        assert( options.has("e") );
        assert( options.hasArgument("e") );

        String configPath = options.valueOf("c").toString();
        String rootDir = options.valueOf("r").toString();
        String chainEnvironment = options.valueOf("e").toString();
        Wallets ws = new Wallets(configPath,rootDir,chainEnvironment);

        if ( options.has("w") ) { // create wallets
            ws.provisionWallets();
        } else
        if ( options.has("b") ) { // payoff balances
            String pwd = options.valueOf("b").toString();
            ws.payOff(pwd);
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
