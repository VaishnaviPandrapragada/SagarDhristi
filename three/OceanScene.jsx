import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import { COLORS } from "../data/mock.js";

/* ==========================================================================
   Floating ocean: a finite slab of water suspended in dark space, with a
   research vessel tracing a slow circuit, a live wake, a weathering oil
   patch and a satellite on orbit above. Built directly on three.js so the
   wave field is a real displaced mesh rather than a shader-faked image.
   ========================================================================== */

export default function OceanScene() {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(COLORS.bg);
    scene.fog = new THREE.FogExp2(COLORS.bg, 0.022);

    const camera = new THREE.PerspectiveCamera(42, mount.clientWidth / mount.clientHeight, 0.1, 260);
    camera.position.set(0, 16, 36);

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    /* ---------------- lights ---------------- */
    scene.add(new THREE.AmbientLight(0x1b4a5f, 1.15));
    const key = new THREE.DirectionalLight(0xa8e6fb, 1.25);
    key.position.set(14, 26, 10);
    scene.add(key);
    const rim = new THREE.PointLight(0x35c9f5, 2.4, 70);
    rim.position.set(-16, 9, -12);
    scene.add(rim);
    const oilLight = new THREE.PointLight(0xd99a3d, 1.6, 22);
    oilLight.position.set(10, 3.5, -6);
    scene.add(oilLight);

    /* ---------------- ocean slab ---------------- */
    const W = 60, D = 60, SEG = 108;
    const surfaceGeo = new THREE.PlaneGeometry(W, D, SEG, SEG);
    surfaceGeo.rotateX(-Math.PI / 2);
    const base = Float32Array.from(surfaceGeo.attributes.position.array);

    const surfaceMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color(COLORS.ocean),
      emissive: new THREE.Color(0x07222f),
      specular: new THREE.Color(0x9fe8ff),
      shininess: 80,
      side: THREE.DoubleSide,
    });
    const surface = new THREE.Mesh(surfaceGeo, surfaceMat);
    scene.add(surface);

    // Slab sides + underside give the water visible depth, so it reads as a
    // floating volume rather than a plane.
    const slabGeo = new THREE.BoxGeometry(W, 4.2, D);
    const slabMat = new THREE.MeshPhongMaterial({
      color: new THREE.Color("#052436"),
      emissive: new THREE.Color(0x03151f),
      transparent: true,
      opacity: 0.92,
      shininess: 20,
    });
    const slab = new THREE.Mesh(slabGeo, slabMat);
    slab.position.y = -2.15;
    scene.add(slab);

    const slabEdge = new THREE.LineSegments(
      new THREE.EdgesGeometry(slabGeo),
      new THREE.LineBasicMaterial({ color: 0x35c9f5, transparent: true, opacity: 0.16 })
    );
    slabEdge.position.y = -2.15;
    scene.add(slabEdge);

    // Faint survey grid: the satellite-intelligence cue.
    const gridGeo = new THREE.PlaneGeometry(W, D, 20, 20);
    gridGeo.rotateX(-Math.PI / 2);
    const grid = new THREE.Mesh(
      gridGeo,
      new THREE.MeshBasicMaterial({ color: 0x35c9f5, wireframe: true, transparent: true, opacity: 0.05 })
    );
    grid.position.y = 0.05;
    scene.add(grid);

    const wave = (x, z, t) =>
      Math.sin(x * 0.18 + t * 0.9) * 0.5 +
      Math.sin(z * 0.23 - t * 0.7) * 0.42 +
      Math.sin((x + z) * 0.12 + t * 0.42) * 0.32 +
      Math.sin(x * 0.05 - z * 0.06 + t * 0.24) * 0.46;

    /* ---------------- oil patch ---------------- */
    const oilShape = new THREE.Shape();
    for (let i = 0; i <= 26; i++) {
      const a = (i / 26) * Math.PI * 2;
      const r = 3.3 + Math.sin(a * 3.1) * 0.75 + Math.cos(a * 5.4) * 0.42;
      const px = Math.cos(a) * r * 1.35;
      const py = Math.sin(a) * r * 0.6;
      i === 0 ? oilShape.moveTo(px, py) : oilShape.lineTo(px, py);
    }
    const oilGeo = new THREE.ShapeGeometry(oilShape, 10);
    oilGeo.rotateX(-Math.PI / 2);
    const oil = new THREE.Mesh(
      oilGeo,
      new THREE.MeshPhongMaterial({
        color: new THREE.Color(COLORS.oil),
        emissive: new THREE.Color(0x4a2f0c),
        transparent: true,
        opacity: 0.78,
        shininess: 40,
        side: THREE.DoubleSide,
      })
    );
    oil.position.set(11, 0.14, -6);
    oil.rotation.y = -0.4;
    scene.add(oil);

    /* ---------------- research vessel ---------------- */
    const boat = new THREE.Group();
    const hullMat = new THREE.MeshPhongMaterial({ color: 0xeaf7fc, emissive: 0x0d2733, shininess: 70 });
    const trimMat = new THREE.MeshPhongMaterial({ color: 0x35c9f5, emissive: 0x0a2733, shininess: 90 });

    const hullShape = new THREE.Shape();
    hullShape.moveTo(-1.6, -0.32);
    hullShape.lineTo(1.05, -0.32);
    hullShape.lineTo(1.75, 0);
    hullShape.lineTo(1.05, 0.32);
    hullShape.lineTo(-1.6, 0.32);
    hullShape.closePath();
    const hullGeo = new THREE.ExtrudeGeometry(hullShape, { depth: 0.52, bevelEnabled: false });
    hullGeo.rotateX(Math.PI / 2);
    hullGeo.translate(0, 0.2, -0.26);
    boat.add(new THREE.Mesh(hullGeo, hullMat));

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.5, 0.62), trimMat);
    cabin.position.set(-0.35, 0.56, 0);
    boat.add(cabin);
    const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.34, 0.5), hullMat);
    bridge.position.set(-0.35, 0.95, 0);
    boat.add(bridge);
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.028, 0.028, 1.1, 6), trimMat);
    mast.position.set(-0.35, 1.6, 0);
    boat.add(mast);
    const beacon = new THREE.Mesh(
      new THREE.SphereGeometry(0.07, 8, 8),
      new THREE.MeshBasicMaterial({ color: 0xbaf1ff })
    );
    beacon.position.set(-0.35, 2.16, 0);
    boat.add(beacon);
    boat.scale.setScalar(1.2);
    scene.add(boat);

    const boatAt = (t) => {
      const a = t * 0.2;
      return new THREE.Vector3(Math.cos(a) * 16 - 3, 0, Math.sin(a) * 11 + 3);
    };

    /* ---------------- wake ---------------- */
    const STEPS = 52;
    const wakeGeo = new THREE.BufferGeometry();
    const wakePos = new Float32Array(STEPS * 6);
    const wakeCol = new Float32Array(STEPS * 6);
    const idx = [];
    for (let i = 0; i < STEPS - 1; i++) idx.push(i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2);
    wakeGeo.setAttribute("position", new THREE.BufferAttribute(wakePos, 3));
    wakeGeo.setAttribute("color", new THREE.BufferAttribute(wakeCol, 3));
    wakeGeo.setIndex(idx);
    const wake = new THREE.Mesh(
      wakeGeo,
      new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.6, side: THREE.DoubleSide, depthWrite: false })
    );
    scene.add(wake);
    const history = [];
    const foam = new THREE.Color(0xe4f9ff);
    const seaCol = new THREE.Color(COLORS.ocean);

    /* ---------------- mist ---------------- */
    const N = 320;
    const mistGeo = new THREE.BufferGeometry();
    const mistPos = new Float32Array(N * 3);
    const mistRate = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      mistPos[i * 3] = (Math.random() - 0.5) * 56;
      mistPos[i * 3 + 1] = Math.random() * 9;
      mistPos[i * 3 + 2] = (Math.random() - 0.5) * 56;
      mistRate[i] = 0.12 + Math.random() * 0.26;
    }
    mistGeo.setAttribute("position", new THREE.BufferAttribute(mistPos, 3));
    const mist = new THREE.Points(
      mistGeo,
      new THREE.PointsMaterial({ color: 0x9fe0f7, size: 0.1, transparent: true, opacity: 0.38, blending: THREE.AdditiveBlending, depthWrite: false })
    );
    scene.add(mist);

    /* ---------------- satellite + orbit ---------------- */
    const orbit = new THREE.Mesh(
      new THREE.TorusGeometry(27, 0.018, 6, 120),
      new THREE.MeshBasicMaterial({ color: 0x35c9f5, transparent: true, opacity: 0.11 })
    );
    orbit.rotation.x = Math.PI / 2.3;
    orbit.position.y = 8;
    scene.add(orbit);

    const sat = new THREE.Group();
    sat.add(new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.22, 0.22), new THREE.MeshBasicMaterial({ color: 0xdff6ff })));
    const panelMat = new THREE.MeshBasicMaterial({ color: 0x1f7fa8, side: THREE.DoubleSide });
    [-0.42, 0.42].forEach((x) => {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(0.52, 0.2), panelMat);
      p.position.x = x;
      sat.add(p);
    });
    scene.add(sat);

    // Downlink beam, swept slowly across the slab.
    const beamGeo = new THREE.ConeGeometry(2.6, 1, 20, 1, true);
    const beam = new THREE.Mesh(
      beamGeo,
      new THREE.MeshBasicMaterial({ color: 0x35c9f5, transparent: true, opacity: 0.045, side: THREE.DoubleSide, depthWrite: false })
    );
    scene.add(beam);

    /* ---------------- loop ---------------- */
    const clock = new THREE.Clock();
    let raf;

    function frame() {
      const t = reduceMotion ? 6 : clock.getElapsedTime();

      const pos = surfaceGeo.attributes.position;
      for (let i = 0; i < pos.count; i++) {
        pos.array[i * 3 + 1] = wave(base[i * 3], base[i * 3 + 2], t);
      }
      pos.needsUpdate = true;
      surfaceGeo.computeVertexNormals();

      const p = boatAt(t);
      const ahead = boatAt(t + 0.08);
      p.y = wave(p.x, p.z, t) + 0.14;
      boat.position.copy(p);
      boat.lookAt(ahead.x, p.y, ahead.z);
      boat.rotation.z = Math.sin(t * 1.5) * 0.045;
      boat.rotation.x += Math.sin(t * 1.15) * 0.03;

      oil.position.y = wave(11, -6, t) * 0.35 + 0.12;
      oil.rotation.y = -0.4 + Math.sin(t * 0.3) * 0.05;
      oilLight.intensity = 1.4 + Math.sin(t * 1.6) * 0.22;

      history.unshift({ x: p.x, y: p.y, z: p.z, dir: Math.atan2(ahead.x - p.x, ahead.z - p.z) });
      if (history.length > STEPS) history.pop();
      for (let i = 0; i < STEPS; i++) {
        const h = history[Math.min(i, history.length - 1)];
        const age = i / STEPS;
        const spread = 0.08 + age * 1.7;
        const ox = Math.cos(h.dir) * spread;
        const oz = -Math.sin(h.dir) * spread;
        const y = wave(h.x, h.z, t) + 0.06;
        wakePos[i * 6] = h.x + ox; wakePos[i * 6 + 1] = y; wakePos[i * 6 + 2] = h.z + oz;
        wakePos[i * 6 + 3] = h.x - ox; wakePos[i * 6 + 4] = y; wakePos[i * 6 + 5] = h.z - oz;
        const c = foam.clone().lerp(seaCol, age * age);
        for (const o of [0, 3]) {
          wakeCol[i * 6 + o] = c.r; wakeCol[i * 6 + o + 1] = c.g; wakeCol[i * 6 + o + 2] = c.b;
        }
      }
      wakeGeo.attributes.position.needsUpdate = true;
      wakeGeo.attributes.color.needsUpdate = true;

      const mp = mistGeo.attributes.position;
      for (let i = 0; i < N; i++) {
        mp.array[i * 3 + 1] += mistRate[i] * 0.012;
        if (mp.array[i * 3 + 1] > 9.5) mp.array[i * 3 + 1] = 0;
      }
      mp.needsUpdate = true;

      const sa = t * 0.22;
      sat.position.set(Math.cos(sa) * 27, 8 + Math.sin(sa * 0.7) * 1.4, Math.sin(sa) * 27 * Math.cos(Math.PI / 2.3));
      sat.rotation.y = -sa;
      beam.position.set(sat.position.x * 0.45, 4, sat.position.z * 0.45);
      beam.scale.set(1, 8, 1);
      orbit.rotation.z = t * 0.04;

      camera.position.x = Math.sin(t * 0.07) * 3.4;
      camera.position.y = 16 + Math.sin(t * 0.11) * 0.7;
      camera.lookAt(0, -0.6, 0);

      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    }
    frame();

    const ro = new ResizeObserver(() => {
      if (!mount.clientWidth) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    });
    ro.observe(mount);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      if (renderer.domElement.parentNode === mount) mount.removeChild(renderer.domElement);
      scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
      });
      renderer.dispose();
    };
  }, []);

  return <div ref={mountRef} style={{ position: "absolute", inset: 0 }} aria-hidden="true" />;
}
