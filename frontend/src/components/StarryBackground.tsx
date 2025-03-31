'use client'

import { useEffect } from 'react';

export function StarryBackground() {
  useEffect(() => {
    const starCount = 200; // Increased star count
    const shootingStarInterval = 4000; // More frequent shooting stars

    function createStar() {
      const star = document.createElement("div");
      star.className = "star";
      star.style.top = `${Math.random() * 100}%`;
      star.style.left = `${Math.random() * 100}%`;
      // Random star sizes for more depth
      const size = Math.random() * 3;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      document.getElementById("stars")?.appendChild(star);
    }

    function createShootingStar() {
      const shootingStar = document.createElement("div");
      shootingStar.className = "shooting-star";
      shootingStar.style.top = `${Math.random() * 50}%`; // Keep in upper half
      shootingStar.style.left = `${Math.random() * 100}%`;
      const starsContainer = document.getElementById("stars");
      if (starsContainer) {
        starsContainer.appendChild(shootingStar);
        setTimeout(() => shootingStar.remove(), 1000);
      }
    }

    function generateStars() {
      for (let i = 0; i < starCount; i++) {
        createStar();
      }
    }

    function randomizeShootingStars() {
      const interval = Math.random() * shootingStarInterval;
      setTimeout(() => {
        createShootingStar();
        randomizeShootingStars();
      }, interval);
    }

    generateStars();
    randomizeShootingStars();

    return () => {
      const stars = document.getElementById("stars");
      if (stars) stars.innerHTML = '';
    };
  }, []);

  return <div id="stars" className="absolute inset-0 overflow-hidden" />;
}
