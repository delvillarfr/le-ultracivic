'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import ValueProps from '@/components/ValueProps';
import MessageSection from '@/components/MessageSection';
import Actions from '@/components/Actions';
import HistoryTable from '@/components/HistoryTable';
import Footer from '@/components/Footer';
import Modal from '@/components/Modal';
import WalletConnection from '@/components/WalletConnection';
import PaymentModal from '@/components/PaymentModal';
import { useWalletConnection } from '@/hooks/useWalletConnection';
import { useEthPrice } from '@/hooks/useEthPrice';
import { useReservation } from '@/hooks/useReservation';

export default function Home() {
  const [allowanceValue, setAllowanceValue] = useState(999);
  const [messageValue, setMessageValue] = useState('');
  const [priceCalc, setPriceCalc] = useState(23976);
  const [tokenCalc, setTokenCalc] = useState(999);
  const [impactCalc, setImpactCalc] = useState(229770);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showWalletConnection, setShowWalletConnection] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { isReady, address } = useWalletConnection();
  const { ethPriceUSD, calculateEthAmount } = useEthPrice();
  const { isReserving, reservationError, reservation, reserveAllowances, clearReservation } = useReservation();

  const updateCalculations = (allowance: number) => {
    const price = allowance * 24;
    const tokens = allowance;
    const impact = allowance * 230;
    
    setPriceCalc(price);
    setTokenCalc(tokens);
    setImpactCalc(impact);
  };

  const handleAllowanceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = parseInt(e.target.value) || 0;
    
    if (value < 1) value = 1;
    if (value > 99) value = 99;
    
    setAllowanceValue(value);
    updateCalculations(value);
    setErrorMessage('');
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageValue(e.target.value);
    setErrorMessage('');
  };

  const handleDoItClick = async () => {
    const allowance = allowanceValue;
    const message = messageValue.trim();
    
    if (allowance < 1 || allowance > 99) {
      setErrorMessage('Please enter a valid allowance amount (1-99).');
      return;
    }
    
    if (!message) {
      setErrorMessage('Please enter a message for history.');
      return;
    }
    
    setErrorMessage('');
    
    if (!isReady) {
      setShowWalletConnection(true);
      return;
    }
    
    // Reserve allowances before showing payment modal
    const reservationResult = await reserveAllowances({
      num_allowances: allowance,
      message: message,
      wallet: address!
    });
    
    if (reservationResult) {
      setShowPaymentModal(true);
    } else {
      setErrorMessage(reservationError || 'Failed to reserve allowances');
    }
  };

  const handleWhatClick = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };
  
  const handleWalletConnected = async () => {
    setShowWalletConnection(false);
    
    // Reserve allowances after wallet connection
    const reservationResult = await reserveAllowances({
      num_allowances: allowanceValue,
      message: messageValue.trim(),
      wallet: address!
    });
    
    if (reservationResult) {
      setShowPaymentModal(true);
    } else {
      setErrorMessage(reservationError || 'Failed to reserve allowances');
    }
  };

  useEffect(() => {
    updateCalculations(allowanceValue);
  }, []);

  return (
    <>
      <Head>
        <title>Ultra Civic</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>
      
      <div className={`container ${showPaymentModal ? 'blurred' : ''}`}>
        <Header />
        <HeroSection 
          allowanceValue={allowanceValue}
          onAllowanceChange={handleAllowanceChange}
        />
        <ValueProps 
          priceCalc={priceCalc}
          tokenCalc={tokenCalc}
          impactCalc={impactCalc}
          allowanceValue={allowanceValue}
        />
        <MessageSection 
          messageValue={messageValue}
          onMessageChange={handleMessageChange}
        />
        {(errorMessage || reservationError) && (
          <div className="error-message">
            {errorMessage || reservationError}
          </div>
        )}
        {isReserving && (
          <div className="loading-message">
            Reserving allowances...
          </div>
        )}
        <Actions 
          onDoItClick={handleDoItClick}
          onWhatClick={handleWhatClick}
        />
        <HistoryTable />
        <Footer />
      </div>
      
      <Modal isOpen={isModalOpen} onClose={handleCloseModal}>
        <h2>What is Ultra Civic?</h2>
        <p>Ultra Civic allows you to buy and retire polluters' legal rights to emit carbon dioxide, directly reducing global emissions.</p>
        <p>When you purchase CO2 allowances, you:</p>
        <ul>
          <li>Remove pollution rights from the market permanently</li>
          <li>Earn PR tokens as proof of your environmental impact</li>
          <li>Leave a message for history about your contribution</li>
        </ul>
        <p>Each ton of CO2 allowances you retire makes a real difference in fighting climate change.</p>
      </Modal>
      
      <Modal isOpen={showWalletConnection} onClose={() => setShowWalletConnection(false)}>
        <h2>Connect Your Wallet</h2>
        <p>Connect your wallet to proceed with the payment.</p>
        <WalletConnection onConnected={handleWalletConnected} />
      </Modal>
      
      <PaymentModal 
        isOpen={showPaymentModal}
        onClose={() => {
          setShowPaymentModal(false);
          clearReservation();
        }}
        allowances={allowanceValue}
        message={messageValue}
        reservation={reservation}
      />
    </>
  );
}
