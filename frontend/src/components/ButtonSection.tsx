'use client'

import { useState } from 'react'
import { DoItButton, WhatButton } from './svg'
import Modal from './Modal'

export default function ButtonSection() {
  const [showModal, setShowModal] = useState(false)

  const handleDoIt = () => {
    console.log('Do It button clicked')
  }

  const handleWhat = () => {
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
  }

  return (
    <>
      <div className="flex justify-center gap-8">
        <button
          onClick={handleDoIt}
          className="transition-transform hover:scale-105 active:scale-95"
          aria-label="Do It"
        >
          <DoItButton />
        </button>
        
        <button
          onClick={handleWhat}
          className="transition-transform hover:scale-105 active:scale-95"
          aria-label="What is this?"
        >
          <WhatButton />
        </button>
      </div>
      
      <Modal isOpen={showModal} onClose={closeModal} />
    </>
  )
}