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
import org.web3j.protocol.core.methods.response.EthAccounts;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.protocol.exceptions.TransactionException;
import org.web3j.protocol.http.HttpService;
import org.web3j.crypto.Credentials;
import org.web3j.tx.Transfer;
import org.web3j.utils.Convert;
import org.web3j.utils.Numeric;


import java.math.BigInteger;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

import static org.junit.Assert.assertThat;
import static org.hamcrest.core.Is.is;
import static org.hamcrest.core.IsNot.not;
import static org.web3j.codegen.Console.exitError;

public class HuhulaTest {

    private static final Logger LOG = LoggerFactory.getLogger(HuhulaTest.class);

//    public static final BigInteger GAS_LIMIT = BigInteger.valueOf(7_300_000);

    public static final BigInteger GAS_PRICE = Numeric.toBigInt("2000000000");

    public static final BigInteger GAS_LIMIT = BigInteger.valueOf(7_984_452);

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

//    @Test
//    @Category(com.huhula.Huhula.class)
//    public void no_testDeployContract() {
//        String testrpc_url = "http://localhost:7546";
////        Credentials credentials = Credentials.create(
////                SampleKeys.PRIVATE_KEY_STRING, SampleKeys.PUBLIC_KEY_STRING);
//        Credentials credentials = Credentials.create(SampleKeys.PRIVATE_KEY_STRING);
//
//        Web3j web3j = Web3j.build(new HttpService(testrpc_url));
//        try {
//            EthAccounts ea = web3j.ethAccounts().send();
//            System.out.println(" web3j.ethAccounts() "+ ea);
//            for (String ac : ea.getAccounts()) {
//                System.out.println("ac:"+ac);
//            }
//
//  //          Huhula.deploy
//            RemoteCall<Huhula>  huhu = Huhula.deploy(Web3j.build(new HttpService(testrpc_url)),credentials,
//                    GAS_PRICE, GAS_LIMIT);
////                    SampleKeys.gasPrice, SampleKeys.gasLimit);
//            System.out.println("remote_call huhu "+huhu);
//
//            Huhula hu1 = huhu.send();
//            hu1.buyBackRate();
//        } catch ( Throwable th ) {
//            th.printStackTrace();
//        }
//    }

    @Test
    @Category(com.huhula.contract.HuhulaSale.class)
    public void testConfig() {
        Settings conf = new Settings(".conf","ganache");
        assertThat(conf.getString("huhula.dbaddress"),  not(""));
        assertThat(conf.getString("wallets.dbaddress"),  not(""));
        assertThat(conf.getString("huhula.dbport"),  is("26257"));
        assertThat(conf.getString("wallets.dbport"),  is("26257"));
        assertThat(conf.getString("ganache.rpc"),  not(""));
    }

    @Test
    @Category(com.huhula.contract.HuhulaSale.class)
    public void testLoadContractGanache() {
        Settings conf = new Settings(".conf","ganache");;

//        Credentials credentials = Credentials.create(
//                SampleKeys.PRIVATE_KEY_STRING, SampleKeys.PUBLIC_KEY_STRING);

        Credentials credentials = Credentials.create(SampleKeys.PRIVATE_KEY_STRING);

        Web3j web3j = Web3j.build(new HttpService(conf.getRpc()));
        try {
            EthAccounts ea = web3j.ethAccounts().send();
            System.out.println(" web3j.ethAccounts() "+ ea);
            for (String ac : ea.getAccounts()) {
                LOG.info("ac:"+ac);
            }

            HuhulaSale huhu = HuhulaSale.load(conf.getContract(), Web3j.build(new HttpService(conf.getRpc())),credentials, GAS_PRICE, GAS_LIMIT);
//                    SampleKeys.gasPrice, SampleKeys.gasLimit);
            LOG.info("remote_call huhu "+huhu);


            String bbrte= huhu.buyBackRate().send().toString();
            LOG.info("bbrte="+bbrte);

            String tme= huhu.closingTime().send().toString();
            LOG.info("tme="+tme);

            String rte= huhu.rate().send().toString();
            LOG.info("rte="+rte);

            String owner= huhu.owner().send().toString();
            LOG.info("owner="+owner);

            String token= huhu.token().send().toString();
            LOG.info("token="+token);

            try {
                Convert.Unit transferUnit = Convert.Unit.ETHER;
                BigDecimal amountToTransfer = new BigDecimal("1");
                BigDecimal amountInWei = Convert.toWei(amountToTransfer, transferUnit);

                Future<TransactionReceipt> future = Transfer.sendFunds(
                        web3j, credentials,
                        conf.getPool(), amountInWei, Convert.Unit.WEI)
                        .sendAsync();

                while (!future.isDone()) {
                    LOG.info(".");
                    Thread.sleep(500);
                }

                LOG.info("$%n%n");
                String status = future.get().getStatus();
                LOG.info("send status="+status);
            } catch (InterruptedException | ExecutionException | TransactionException | IOException e) {
                exitError("Problem encountered transferring funds: \n" + e.getMessage());
            }
            // throw new RuntimeException("Application exit failure");

            BigInteger tokens = new BigInteger("1");
            CompletableFuture<TransactionReceipt> cf = huhu.grantTokens(conf.getPool(),tokens).sendAsync();
            while (!cf.isDone()) {
                LOG.info(".");
                Thread.sleep(500);
            }
            String status = cf.get().getStatus();
            LOG.info("status="+status);
        } catch ( Throwable th ) {
            exitError("Problem encountered communicating with contract:\n"+ th.getMessage());
        }
    }

}