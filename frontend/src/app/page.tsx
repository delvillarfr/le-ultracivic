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

export default function Home() {
  const [allowanceValue, setAllowanceValue] = useState(999);
  const [messageValue, setMessageValue] = useState('');
  const [priceCalc, setPriceCalc] = useState(23976);
  const [tokenCalc, setTokenCalc] = useState(999);
  const [impactCalc, setImpactCalc] = useState(229770);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

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

  const handleDoItClick = () => {
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
    alert(`Starting payment flow for ${allowance} tons of CO2 allowances.\nMessage: "${message}"`);
    
    console.log('Payment flow initiated:', {
      allowance: allowance,
      price: allowance * 24,
      message: message
    });
  };

  const handleWhatClick = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
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
      
      <div className="container">
        <Header />
        <HeroSection 
          allowanceValue={allowanceValue}
          onAllowanceChange={handleAllowanceChange}
        />
        <ValueProps 
          priceCalc={priceCalc}
          tokenCalc={tokenCalc}
          impactCalc={impactCalc}
        />
        <MessageSection 
          messageValue={messageValue}
          onMessageChange={handleMessageChange}
        />
        {errorMessage && (
          <div className="error-message">
            {errorMessage}
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
    </>
  );
}
