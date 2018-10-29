package com.huhula.credentials;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.web3j.utils.Numeric;

import java.io.File;
import java.math.BigInteger;

public class Settings {

    private static final Logger LOG = LoggerFactory.getLogger(Settings.class);

    private Config config;
    private String chain;

    public Settings(String _configPath, String _chain) {
        chain = _chain;
        Config defaultConfig = ConfigFactory.parseFile(new File(_configPath+"/"+"defaults.conf"));
        Config chainConfig = ConfigFactory.parseFile(new File(_configPath+"/env/"+_chain+".conf"));
        Config userConfig = ConfigFactory.parseFile(new File(_configPath+"/"+"user.conf"));

        config = userConfig
                .withFallback(chainConfig)
                .withFallback(defaultConfig)
                .resolve();
    }

    public String getString(String vn) {
        return config.getString("conf."+vn);
    }

    public String getTempDir() {
        return getString("tempDir");
    }

    public String getPoolUtcFile() {
        return getChain("pool_utc_file");
    }

    public String getOwnerUtcFile() {
        return getChain("owner_utc_file");
    }

    public double getMinBalance() {
        return 1e-9;
    }


    public String getRpc() {
        return getChain("rpc");
    }

    public String getSaleAddress() {
        return getChain("sale");
    }

    public String getTokenAddress() {
        return getChain("token");
    }


    public String getOwner() {
        return getChain("owner");
    }

    public String getFeeFrom() {
        return getChain("fee_from");
    }

    public String getTestTo() {
        return getChain("test_to");
    }

    public BigInteger getGasPrice() {
       return BigInteger.valueOf(Long.valueOf(getChain("gas_price")));
    }

    public BigInteger getGasLimit() {
        return BigInteger.valueOf(Long.valueOf(getChain("gas_limit")));
    }

    public static final BigInteger GAS_LIMIT = BigInteger.valueOf(7984452);

    public String getPool() {
        return getChain("pool");
    }

    private String getChain(String vn) {
        String var = "conf."+chain+"."+vn;
        String res= config.getString(var);
        LOG.debug("config variable:"+var+" value:"+res);
        return res;
    }

    public String getPrivateKey() {
        return getChain("private");
    }

}
