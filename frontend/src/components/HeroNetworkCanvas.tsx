"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HeroNetworkCanvas() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    const mouse = new THREE.Vector2(0, 0);
    const target = new THREE.Vector2(0, 0);
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    const onDocumentMouseMove = (event: MouseEvent) => {
      mouse.x = (event.clientX - windowHalfX) * 0.0005;
      mouse.y = (event.clientY - windowHalfY) * 0.0005;
    };
    
    document.addEventListener("mousemove", onDocumentMouseMove, false);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      400
    );
    camera.position.z = 72;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const nodeCount = 120;
    const positions = new Float32Array(nodeCount * 3);

    for (let i = 0; i < nodeCount; i += 1) {
      const radius = 26 + Math.random() * 14;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
    }

    const nodeGeometry = new THREE.BufferGeometry();
    nodeGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const nodeMaterial = new THREE.PointsMaterial({
      color: 0x22d3ee,
      size: 0.9,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.85,
    });

    const nodes = new THREE.Points(nodeGeometry, nodeMaterial);
    group.add(nodes);

    const alertCount = 14;
    const alertPositions = new Float32Array(alertCount * 3);

    for (let i = 0; i < alertCount; i += 1) {
      const idx = Math.floor(Math.random() * nodeCount) * 3;
      alertPositions[i * 3] = positions[idx];
      alertPositions[i * 3 + 1] = positions[idx + 1];
      alertPositions[i * 3 + 2] = positions[idx + 2];
    }

    const alertGeometry = new THREE.BufferGeometry();
    alertGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(alertPositions, 3)
    );

    const alertMaterial = new THREE.PointsMaterial({
      color: 0xf43f5e,
      size: 1.6,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.95,
    });

    const alerts = new THREE.Points(alertGeometry, alertMaterial);
    group.add(alerts);

    const segmentCount = 160;
    const linePositions = new Float32Array(segmentCount * 6);

    for (let i = 0; i < segmentCount; i += 1) {
      const a = Math.floor(Math.random() * nodeCount) * 3;
      const b = Math.floor(Math.random() * nodeCount) * 3;
      linePositions[i * 6] = positions[a];
      linePositions[i * 6 + 1] = positions[a + 1];
      linePositions[i * 6 + 2] = positions[a + 2];
      linePositions[i * 6 + 3] = positions[b];
      linePositions[i * 6 + 4] = positions[b + 1];
      linePositions[i * 6 + 5] = positions[b + 2];
    }

    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(linePositions, 3)
    );

    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.35,
    });

    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    group.add(lines);

    let frameId: number;

    const animate = () => {
      if (!prefersReducedMotion) {
        target.x = mouse.x;
        target.y = mouse.y;
        
        group.rotation.y += 0.0008 + (target.x - group.rotation.y) * 0.05;
        group.rotation.x += 0.0004 + (target.y - group.rotation.x) * 0.05;
      }
      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("mousemove", onDocumentMouseMove);
      window.cancelAnimationFrame(frameId);
      nodeGeometry.dispose();
      alertGeometry.dispose();
      lineGeometry.dispose();
      nodeMaterial.dispose();
      alertMaterial.dispose();
      lineMaterial.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 pointer-events-none"
      aria-hidden="true"
    />
  );
}
