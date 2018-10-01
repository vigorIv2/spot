package com.huhula;


// import com.sun.xml.internal.ws.util.CompletedFuture;
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

public class HuhulaTest {

    private static final Logger LOG = LoggerFactory.getLogger(HuhulaTest.class);
 //   private static final String chain = "rinkeby";
    private static final String chain = "ganache";

//    @Test
//    @Category(com.huhula.Huhula.class)
//    public void testSlow() {
//        System.out.println("slow");
//    }
//
//    @Test
//    @Category(com.huhula.Huhula.class)
//    public void testSlower() {
//        System.out.println("slower");
//    }


    @Test
    @Category(com.huhula.contract.HuhulaSale.class)
    public void testConfig() {
        Settings conf = new Settings(".conf",chain);
        assertThat(conf.getString("huhula.dbaddress"),  not(""));
        assertThat(conf.getString("wallets.dbaddress"),  not(""));
        assertThat(conf.getString("huhula.dbport"),  is("26257"));
        assertThat(conf.getString("wallets.dbport"),  is("26257"));
        assertThat(conf.getString(chain+".rpc"),  not(""));
    }

    private void logBalance(Web3j web3j, String account) {
        // send asynchronous requests to get balance
        try {
            EthGetBalance ethGetBalance = web3j
                    .ethGetBalance(account, DefaultBlockParameterName.LATEST)
                    .sendAsync()
                    .get();

            BigInteger wei = ethGetBalance.getBalance();
            LOG.info("Account "+account+" balance="+wei.toString());
        } catch (InterruptedException | ExecutionException e) {
            LOG.error("Problem encountered receiving version", e);
        }
    }
    @Test
    @Category(com.huhula.contract.HuhulaSale.class)
    public void testLoadContractChain() {
        Settings conf = new Settings(".conf",chain);;

//        Credentials credentials = Credentials.create(
//                conf.getPrivateKey(), conf.getPublicKey());

        Credentials credentials = Credentials.create(conf.getPrivateKey());

        //Credentials credentials = WalletUtils.loadCredentials("password", "/path/to/walletfile");
        //Web3j web3 = Web3j.build(new UnixIpcService("/path/to/socketfile"));
        Web3j web3j = Web3j.build(new HttpService(conf.getRpc()));

        try {
            Web3ClientVersion web3ClientVersion = web3j.web3ClientVersion().send();
            String clientVersion = web3ClientVersion.getWeb3ClientVersion();
            LOG.info("web3j version "+clientVersion);

            Web3ClientVersion web3ClientVersionAsync = web3j.web3ClientVersion().sendAsync().get();

            String clientVersionAsinc = web3ClientVersionAsync.getWeb3ClientVersion();
            LOG.info("web3j version Async "+clientVersionAsinc);
        } catch (InterruptedException | ExecutionException | IOException e) {
            LOG.error("Problem encountered receiving version", e);
        }


        try {
            EthAccounts ea = web3j.ethAccounts().send();
            LOG.info(" web3j.ethAccounts() "+ ea);
            for (String ac : ea.getAccounts()) {
                LOG.info("ac:"+ac);
            }

            ClientTransactionManager clientTransactionManager0 =
                    new ClientTransactionManager(web3j, conf.getFeeFrom());


            LOG.info("Contract addr "+conf.getSaleAddress());

            LOG.info("From addr "+clientTransactionManager0.getFromAddress());


            LOG.info("Config Gas Price = "+conf.getGasPrice());
            LOG.info("Config Gas Limit = "+conf.getGasLimit());

            HuhulaSale huhu = HuhulaSale.load(conf.getSaleAddress(), Web3j.build(new HttpService(conf.getRpc())),clientTransactionManager0, conf.getGasPrice(), conf.getGasLimit());
            LOG.info("remote_call huhu "+huhu);


            String tme= huhu.closingTime().send().toString();
            LOG.info("tme="+tme);

            String bbrte= huhu.buyBackRate().send().toString();
            LOG.info("bbrte="+bbrte);


            String rte= huhu.rate().send().toString();
            LOG.info("rte="+rte);

            String owner= huhu.owner().send().toString();
            LOG.info("owner="+owner);

            String token= huhu.token().send().toString();
            LOG.info("token="+token);

            // this works with ganache
            logBalance(web3j,conf.getFeeFrom());
            logBalance(web3j,conf.getTestTo());
            ClientTransactionManager clientTransactionManager =
                    new ClientTransactionManager(web3j, conf.getFeeFrom());

            LOG.debug("From addr "+clientTransactionManager.getFromAddress());

            org.web3j.tx.Transfer tran = new org.web3j.tx.Transfer(web3j, clientTransactionManager);

            LOG.debug("Threshold "+String.valueOf(tran.getSyncThreshold()));

            RemoteCall rc = tran.sendFunds(
                    conf.getTestTo(),
                    BigDecimal.valueOf(0.1),
                    Convert.Unit.ETHER
            );

            LOG.debug("RC="+ String.valueOf(rc.toString()));
            rc.send();

            LOG.debug("after RC="+ String.valueOf(rc.toString()));
            web3j.ethGasPrice().send(); //
//            web3j.ethGetTransactionByHash();
//            web3j.ethGetTransactionReceipt();

            logBalance(web3j,conf.getFeeFrom());
            logBalance(web3j,conf.getTestTo());

            try {
//                Convert.Unit transferUnit = Convert.Unit.ETHER;
//                BigDecimal amountToTransfer = new BigDecimal("1");
//                BigDecimal amountInWei = Convert.toWei(amountToTransfer, transferUnit);


                // https://docs.web3j.io/getting_started.html
//                Admin web3ja = Admin.build(new HttpService(conf.getRpc()));  // defaults to http://localhost:8545/
//                PersonalUnlockAccount personalUnlockAccount = web3ja.personalUnlockAccount(credentials.getAddress(), "").sendAsync().get();
//                if (personalUnlockAccount.accountUnlocked()) {
//                    LOG.info("Account unlocked, sending transaction");
                    // send a transaction

                RemoteCall rc1 = tran.sendFunds(
                        conf.getTestTo(), BigDecimal.valueOf(1.0), Convert.Unit.ETHER);


                LOG.info("before send() rc="+rc1.toString());
                rc1.send();
                LOG.debug("after send  RC="+ String.valueOf(rc.toString()));

                Future<TransactionReceipt> future = Transfer.sendFunds(
                            web3j, credentials,
                            conf.getPool(), BigDecimal.valueOf(1.0), Convert.Unit.ETHER)
                            .sendAsync();

                    while (!future.isDone()) {
                        LOG.info(".");
                        Thread.sleep(500);
                    }
                TransactionReceipt trc = future.get(); // TransactionReceipt
                // trc.
                LOG.info("$%n%n");
                String status = future.toString(); // getStatus();
                LOG.info("send status="+status);
//                } else {
//                    LOG.info("Account failed to unlock");
//                }
            } catch (InterruptedException | TransactionException | IOException e) {
                LOG.error("Problem encountered transferring funds", e);
                throw e;
            }
            // throw new RuntimeException("Application exit failure");

            BigInteger tokens = new BigInteger("1000");
            RemoteCall rca = huhu.grantTokens(conf.getTestTo(),tokens);
            Thread.sleep(500);
            CompletableFuture cf = rca.sendAsync();

            while (!cf.isDone()) {
                LOG.info(".");
                Thread.sleep(500);
            }

            String status = cf.get().toString();
            LOG.info("status="+status);
        } catch ( Throwable th ) {
            LOG.error("Problem encountered communicating with contract", th);
            web3j.shutdown();
        }
    }

}