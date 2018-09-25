package com.huhula.credentials;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;

import java.io.File;

public class Settings {

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

    public String getRpc() {
        return getChain("rpc");
    }

    public String getContract() {
        return getChain("contract");
    }

    public String getToken() {
        return getChain("token");
    }

    public String getOwner() {
        return getChain("owner");
    }

    public String getPool() {
        return getChain("pool");
    }

    private String getChain(String vn) {
        return config.getString("conf."+chain+"."+vn);
    }

}
