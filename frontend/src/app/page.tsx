'use client';

import { useState, useEffect } from 'react';
import Head from 'next/head';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import ValueProps from '@/components/ValueProps';
import MessageSection from '@/components/MessageSection';
import Actions from '@/components/Actions';
import Footer from '@/components/Footer';
import Modal from '@/components/Modal';
import WalletConnection from '@/components/WalletConnection';
import PaymentModal from '@/components/PaymentModal';
import { useWalletConnection } from '@/hooks/useWalletConnection';
import { useEthPrice } from '@/hooks/useEthPrice';
import { useReservation } from '@/hooks/useReservation';
import LoadingButton from '@/components/ui/LoadingButton';
import CONFIG from '@/lib/config';

export default function Home() {
  const [allowanceValue, setAllowanceValue] = useState(CONFIG.DEFAULT_ALLOWANCES);
  const [inputValue, setInputValue] = useState(CONFIG.DEFAULT_ALLOWANCES.toString());
  const [messageValue, setMessageValue] = useState('');
  const [priceCalc, setPriceCalc] = useState(CONFIG.DEFAULT_ALLOWANCES * CONFIG.PRICE_PER_ALLOWANCE_USD);
  const [tokenCalc, setTokenCalc] = useState(CONFIG.DEFAULT_ALLOWANCES * CONFIG.TOKENS_PER_ALLOWANCE);
  const [impactCalc, setImpactCalc] = useState(CONFIG.DEFAULT_ALLOWANCES * CONFIG.SOCIAL_IMPACT_MULTIPLIER);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showWalletConnection, setShowWalletConnection] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const { isReady, address } = useWalletConnection();
  const { ethPriceUSD, calculateEthAmount } = useEthPrice();
  const { isReserving, reservationError, reservation, reserveAllowances, clearReservation } = useReservation();

  const updateCalculations = (allowance: number) => {
    const price = allowance * CONFIG.PRICE_PER_ALLOWANCE_USD;
    const tokens = allowance * CONFIG.TOKENS_PER_ALLOWANCE;
    const impact = allowance * CONFIG.SOCIAL_IMPACT_MULTIPLIER;
    
    setPriceCalc(price);
    setTokenCalc(tokens);
    setImpactCalc(impact);
  };

  const handleAllowanceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value;
    
    // Prevent more than 2 digits
    if (rawValue.length > 2) {
      return;
    }
    
    // Always update the input display value
    setInputValue(rawValue);
    
    // Allow empty string during editing
    if (rawValue === '') {
      setErrorMessage('');
      return;
    }
    
    // Parse the value
    let value = parseInt(rawValue);
    
    // Handle NaN case - don't update anything
    if (isNaN(value)) {
      return;
    }
    
    // Only allow values within valid range
    if (value >= 1 && value <= 99) {
      setAllowanceValue(value);
      updateCalculations(value);
      setErrorMessage('');
    }
  };

  const handleAllowanceBlur = () => {
    // When user finishes editing, ensure we have a valid value
    if (inputValue === '' || parseInt(inputValue) < 1) {
      setInputValue('1');
      setAllowanceValue(1);
      updateCalculations(1);
    }
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageValue(e.target.value);
    setErrorMessage('');
  };

  const handleDoItClick = async () => {
    const allowance = allowanceValue;
    const message = messageValue.trim();
    
    if (allowance < CONFIG.MIN_ALLOWANCES || allowance > CONFIG.MAX_ALLOWANCES) {
      setErrorMessage(`Please enter a valid allowance amount (${CONFIG.MIN_ALLOWANCES}-${CONFIG.MAX_ALLOWANCES}).`);
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
    
    
    // For hackathon demo - skip backend reservation and go straight to payment
    setShowPaymentModal(true);
  };

  const handleWhatClick = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };
  
  const handleWalletConnected = async () => {
    setShowWalletConnection(false);
    
    // Ensure we have a valid address before proceeding
    if (!address) {
      setErrorMessage('Wallet connection failed. Please try again.');
      return;
    }
    
    // Clear any existing errors
    setErrorMessage('');
    
    
    // Reserve allowances after wallet connection
    const reservationResult = await reserveAllowances({
      num_allowances: allowanceValue,
      message: messageValue.trim(),
      wallet: address
    });
    
    if (reservationResult) {
      setShowPaymentModal(true);
    }
    // Don't show error message for reservation failure - just continue
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
          inputValue={inputValue}
          onAllowanceChange={handleAllowanceChange}
          onAllowanceBlur={handleAllowanceBlur}
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
        <div className="actions">
          <LoadingButton 
            onClick={handleDoItClick}
            isLoading={isReserving}
            className="action-btn do-it-btn"
            variant="primary"
          >
            <img src="/media/doit.svg" alt="Do It" className="doit" />
          </LoadingButton>
          <LoadingButton 
            onClick={handleWhatClick}
            className="action-btn what-btn"
            variant="secondary"
          >
            <img src="/media/what.svg" alt="What?" className="what" />
          </LoadingButton>
        </div>
        <Footer />
      </div>
      
      <Modal isOpen={isModalOpen} onClose={handleCloseModal}>
        <div className="what-modal-content">
          <img src="/media/vgn1.svg" alt="Ultra Civic explanation 1" />
          <img src="/media/vgn2.svg" alt="Ultra Civic explanation 2" />
          <img src="/media/vgn3.svg" alt="Ultra Civic explanation 3" />
          <img src="/media/vgn4.svg" alt="Ultra Civic explanation 4" />
          <img src="/media/vgn5.svg" alt="Ultra Civic explanation 5" />
          <img src="/media/vgn6.svg" alt="Ultra Civic explanation 6" />
          <img src="/media/vgn7.svg" alt="Ultra Civic explanation 7" />
          <img src="/media/vgn8.svg" alt="Ultra Civic explanation 8" />
        </div>
      </Modal>
      
      <Modal isOpen={showWalletConnection} onClose={() => setShowWalletConnection(false)}>
        <h2>Connect Your Wallet</h2>
        <p>Connect your wallet to proceed with the payment.</p>
        <WalletConnection 
          onConnected={handleWalletConnected} 
          isConnecting={isReserving}
        />
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
