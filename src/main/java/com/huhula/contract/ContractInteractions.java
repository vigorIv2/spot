package com.huhula.contract;

import com.huhula.credentials.Settings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.web3j.crypto.CipherException;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.EthAccounts;
import org.web3j.protocol.core.methods.response.EthGetBalance;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.protocol.core.methods.response.Web3ClientVersion;
import org.web3j.protocol.exceptions.TransactionException;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.ClientTransactionManager;
import org.web3j.tx.Transfer;
import org.web3j.utils.Convert;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

/*
import org.junit.Test;
import org.junit.experimental.categories.Category;

import java.util.concurrent.Future;


import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsNot.not;
import static org.junit.Assert.assertThat;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.concurrent.CompletableFuture;

import com.huhula.contract.HuhulaSale;
import com.huhula.credentials.Settings;
import com.huhula.credentials.Wallets;
import org.junit.Test;
import org.junit.experimental.categories.Category;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.web3j.abi.datatypes.Address;
import org.web3j.abi.datatypes.generated.Uint256;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.admin.Admin;
import org.web3j.protocol.admin.methods.response.PersonalUnlockAccount;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.RemoteCall;
import org.web3j.protocol.core.methods.response.EthAccounts;
import org.web3j.protocol.core.methods.response.EthGetBalance;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.protocol.core.methods.response.Web3ClientVersion;
import org.web3j.protocol.exceptions.TransactionException;
import org.web3j.protocol.http.HttpService;
import org.web3j.crypto.Credentials;

import org.web3j.tx.ClientTransactionManager;
import org.web3j.tx.Transfer;
import org.web3j.utils.Convert;
import org.web3j.utils.Numeric;


import java.math.BigInteger;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.Assert.assertThat;
import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsNot.not;
import static org.web3j.codegen.Console.exitError;
*/

public class ContractInteractions {

    HuhulaSale sale;
    HuhulaToken token;
    Web3j web3j;
    ClientTransactionManager ctm;
    Settings conf;
    public static double tokenDecilmals = 1000000;

    private static final Logger LOG = LoggerFactory.getLogger(ContractInteractions.class);

    public ContractInteractions(Settings _conf) {
        conf = _conf;
        web3j = Web3j.build(new HttpService(conf.getRpc()));
        ctm = new ClientTransactionManager(web3j, conf.getFeeFrom());
        sale = HuhulaSale.load(conf.getSaleAddress(), Web3j.build(new HttpService(conf.getRpc())),ctm, conf.getGasPrice(), conf.getGasLimit());
        token = HuhulaToken.load(conf.getTokenAddress(), Web3j.build(new HttpService(conf.getRpc())),ctm, conf.getGasPrice(), conf.getGasLimit());
        LOG.info("Contract interactions initialized");
    }

    public Credentials getHuhulaCredentials() {
        return Credentials.create(conf.getPrivateKey());
    }

    public Credentials loadCredentials(String pwd, String fname) {
        Credentials credentials = null;
        try {
            credentials = WalletUtils.loadCredentials(pwd, fname);
        } catch ( IOException | CipherException ce ) {
            LOG.error("Exception while loading credentials from "+fname,ce);
        }
        return credentials;
    }

    public BigInteger getBalance(String account) { // send asynchronous requests to get balance
        BigInteger bal = null;
        try {
            EthGetBalance ethGetBalance = web3j.ethGetBalance(account, DefaultBlockParameterName.LATEST)
                    .sendAsync()
                    .get();

            bal = ethGetBalance.getBalance();
            LOG.info("Account:"+account+" balance:"+bal.toString());
        } catch (InterruptedException | ExecutionException e) {
            LOG.error("Problem encountered requesting balance", e);
        }
        return bal;
    }

    public BigInteger getTokenBalance(String account) { // send asynchronous requests to get balance
        BigInteger bal = null;
        try {
            bal = token.balanceOf(account)
                    .sendAsync()
                    .get();
            LOG.info("Account:"+account+" token balance:"+bal.toString());
        } catch (InterruptedException | ExecutionException e) {
            LOG.error("Problem encountered requesting balance", e);
        }
        return bal;
    }

    public String getWeb3Version() {
        String ver = null;
        try {
            Web3ClientVersion clientVersion = web3j.web3ClientVersion().send();
            ver = clientVersion.getWeb3ClientVersion();
            LOG.info("web3j Client version:" + ver);

            Web3ClientVersion web3ClientVersionAsync = web3j.web3ClientVersion().sendAsync().get();

            String clientVersionAsinc = web3ClientVersionAsync.getWeb3ClientVersion();
            LOG.info("web3j Client version Async:" + clientVersionAsinc);
            assert (ver == clientVersionAsinc);
        } catch (InterruptedException | ExecutionException | IOException e) {
            LOG.error("Problem encountered receiving version", e);
        }
        return ver;
    }

    public HuhulaToken getHuhulaToken() {
        return token;
    }

    public String[] getAccounts() {
        List<String> accs = new ArrayList<String>();
        try {
            EthAccounts ea = web3j.ethAccounts().send();
            LOG.info("web3j.ethAccounts() " + ea);
            for (String ac : ea.getAccounts()) {
                LOG.info("account:" + ac);
                accs.add(ac);
            }
        } catch ( IOException ioe ) {
            LOG.error("Problem encountered loading accounts", ioe);
//            web3j.shutdown();
        }
        return accs.toArray(new String[accs.size()]);
    }

    public boolean isHealthy() {
        assert( sale != null );
        assert( token != null );
        assert( web3j != null );
        assert( ctm != null );
        assert( conf != null );

        if ( getWeb3Version() != null )
            if ( getAccounts().length > 0 )
                return true;
        return false;
    }

    /**
     * to deposit balance of tokence
     * @param value
     * @param account
     * @param creds
     * @return
     */

    public BigDecimal depositToUser(Double value, String account){
        BigDecimal res = null;
        try {
            LOG.debug("Transferring token to account:"+account+" amount:"+value);

            RemoteCall rc = token.transfer(account, BigInteger.valueOf(Math.round(value * tokenDecilmals)));

            Thread.sleep(3000);
            CompletableFuture cf = rc.sendAsync();

            while (!cf.isDone()) {
                LOG.info(".");
                Thread.sleep(1000);
            }

            TransactionReceipt tr = (TransactionReceipt)cf.get();
            String status = tr.toString();
            LOG.info("Transferred token to account:"+account+" amount:"+value+" status:"+status+"; Gas used "+tr.getGasUsed());
            res = new BigDecimal(tr.getGasUsed());
        } catch ( InterruptedException | ExecutionException ie ){
            LOG.error("InterruptedException while sending tokens to "+account,ie);
        }
        return res;
    }

    public BigDecimal withdrawalFromUser(Double value, String account){
        BigDecimal res = null;
        try {
            LOG.debug("Withdrawing token from account:"+account+" amount:"+value);

            RemoteCall rc = token.huhulaReturnToOwner(account, BigInteger.valueOf(Math.round(value * tokenDecilmals)));

            Thread.sleep(3000);
            CompletableFuture cf = rc.sendAsync();

            while (!cf.isDone()) {
                LOG.info(".");
                Thread.sleep(1000);
            }

            TransactionReceipt tr = (TransactionReceipt)cf.get();
            String status = tr.toString();
            LOG.info("Withdrawn token from account:"+account+" amount:"+value+" status:"+status+"; Gas used "+tr.getGasUsed());
            res = new BigDecimal(tr.getGasUsed());
        } catch ( InterruptedException | ExecutionException ie ){
            LOG.error("InterruptedException while withdrawing tokens from "+account,ie);
        }
        return res;
    }

    public void shutdown() {
        web3j.shutdown();
        LOG.info("web3j shutdown");
    }


}
