package com.huhula.contract;

import com.huhula.Huhula;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.Web3jService;
import org.web3j.protocol.ipc.UnixIpcService;
import org.web3j.protocol.ipc.WindowsIpcService;
import org.web3j.protocol.core.DefaultBlockParameter;
import org.web3j.protocol.core.Request;
import org.web3j.protocol.core.Response;
import org.web3j.protocol.core.methods.request.ShhFilter;
import org.web3j.protocol.core.methods.request.Transaction;
import org.web3j.protocol.core.methods.response.*;
import org.web3j.protocol.websocket.events.LogNotification;
import org.web3j.protocol.websocket.events.NewHeadsNotification;
import org.web3j.protocol.websocket.events.Notification;
import rx.Observable;

import java.io.IOException;
import java.math.BigInteger;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public class ContractInteractions {

    Huhula hi = null ;

    public ContractInteractions() {
//        hi = Huhula.load("0x798c96bd84ca90a48e858aa1de478cce4cf6913d", Web3j.build("http://localhost:8545"));
    }

    public Long getPrice() {
        return null;
    }

    public static void main(String [] args) {
        ContractInteractions ci = new ContractInteractions();

    }
}
