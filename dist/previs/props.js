import * as THREE from 'three';

/**
 * Original, low-poly stand-ins for the shooting previsualization.
 * Metres, Y up; actors face +Z. No real person, order or customer data.
 */
export function createProps(scene) {
  const sphere = new THREE.SphereGeometry(1, 10, 6);
  const smallSphere = new THREE.SphereGeometry(1, 8, 5);
  const cylinder = new THREE.CylinderGeometry(1, 1, 1, 8);
  const box = new THREE.BoxGeometry(1, 1, 1);
  const disk = new THREE.CylinderGeometry(1, 1, 1, 24);
  const yAxis = new THREE.Vector3(0, 1, 0);
  const palette = {
    skin: new THREE.MeshStandardMaterial({ color: 0xd2c8bb, roughness: 0.8 }),
    white: new THREE.MeshStandardMaterial({ color: 0xf5f3ee, roughness: 0.78 }),
    gray: new THREE.MeshStandardMaterial({ color: 0x323639, roughness: 0.85 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x171c20, roughness: 0.65 }),
    burgundy: new THREE.MeshStandardMaterial({ color: 0x7e2638, roughness: 0.7 }),
    iron: new THREE.MeshStandardMaterial({ color: 0x242728, metalness: 0.68, roughness: 0.4 }),
    steel: new THREE.MeshStandardMaterial({ color: 0xb4bdc0, metalness: 0.85, roughness: 0.28 }),
    brass: new THREE.MeshStandardMaterial({ color: 0xb5964b, metalness: 0.75, roughness: 0.32 }),
    broth: new THREE.MeshStandardMaterial({ color: 0xcb4423, roughness: 0.26 }),
    meatball: new THREE.MeshStandardMaterial({ color: 0xd2ae85, roughness: 0.83 }),
    tofu: new THREE.MeshStandardMaterial({ color: 0xf1dba9, roughness: 0.9 }),
    leaf: new THREE.MeshStandardMaterial({ color: 0x458943, roughness: 0.8 }),
    screen: new THREE.MeshBasicMaterial({ color: 0x143d41 }),
    ink: new THREE.MeshBasicMaterial({ color: 0xf0eee4 }),
    guide: new THREE.MeshStandardMaterial({ color: 0xbac0bd, roughness: 0.9 }),
    red: new THREE.MeshBasicMaterial({ color: 0xe85b43 }),
  };

  function mesh(parent, geometry, material, position, scale) {
    const result = new THREE.Mesh(geometry, material);
    if (position) result.position.set(...position);
    if (scale) result.scale.set(...scale);
    result.castShadow = true;
    result.receiveShadow = true;
    parent.add(result);
    return result;
  }

  function link(bone, start, end, radius) {
    const direction = new THREE.Vector3().subVectors(end, start);
    const length = direction.length();
    bone.position.copy(start).add(end).multiplyScalar(0.5);
    bone.scale.set(radius, Math.max(0.0001, length), radius);
    bone.quaternion.setFromUnitVectors(yAxis, direction.normalize());
  }

  function makeHand(material = palette.skin) {
    const hand = new THREE.Group();
    hand.name = 'Neutral hand stand-in';
    mesh(hand, sphere, material, [0, 0, 0], [0.033, 0.043, 0.018]);
    for (let index = 0; index < 4; index += 1) {
      mesh(hand, smallSphere, material,
        [-0.023 + index * 0.015, -0.039, 0.002],
        [0.009, 0.032 - Math.abs(index - 1.5) * 0.004, 0.009]);
    }
    const thumb = mesh(hand, smallSphere, material,
      [0.035, -0.005, 0.005], [0.012, 0.028, 0.012]);
    thumb.rotation.z = -0.65;
    return hand;
  }

  function makeActor(name, isHost) {
    const actor = new THREE.Group();
    actor.name = name;
    actor.userData.isNeutralStandIn = true;
    actor.userData.heightMetres = 1.65;
    mesh(actor, sphere, palette.white, [0, 1.19, 0], [0.205, 0.23, 0.125]);
    mesh(actor, sphere, palette.gray, [0, 0.93, 0], [0.17, 0.135, 0.12]);
    mesh(actor, cylinder, palette.skin, [0, 1.41, 0], [0.045, 0.08, 0.045]);
    mesh(actor, sphere, palette.skin, [0, 1.535, 0], [0.105, 0.115, 0.095]);
    for (const side of [-1, 1]) {
      mesh(actor, smallSphere, palette.skin,
        [side * 0.104, 1.535, 0], [0.017, 0.029, 0.018]);
      mesh(actor, smallSphere, palette.dark,
        [side * 0.034, 1.55, 0.088], [0.006, 0.006, 0.004]);
      const hip = new THREE.Vector3(side * 0.093, 0.93, 0);
      const knee = new THREE.Vector3(side * 0.096, 0.52, 0.012);
      const ankle = new THREE.Vector3(side * 0.1, 0.12, 0);
      link(mesh(actor, cylinder, palette.gray), hip, knee, 0.069);
      link(mesh(actor, cylinder, palette.gray), knee, ankle, 0.052);
      mesh(actor, smallSphere, palette.gray, knee.toArray(), [0.063, 0.063, 0.063]);
      mesh(actor, sphere, palette.dark,
        [side * 0.1, 0.055, 0.045], [0.068, 0.055, 0.12]);
    }
    mesh(actor, sphere, palette.skin, [0, 1.532, 0.092], [0.013, 0.019, 0.017]);
    mesh(actor, box, isHost ? palette.burgundy : palette.guide,
      [0.094, 1.28, 0.117], [0.048, 0.022, 0.007]);
    if (isHost) {
      mesh(actor, box, palette.burgundy, [0, 1.035, 0.11], [0.25, 0.026, 0.012]);
    }

    const arms = [-1, 1].map((side) => {
      const shoulder = new THREE.Vector3(side * 0.202, 1.34, 0);
      mesh(actor, smallSphere, palette.white, shoulder.toArray(), [0.068, 0.068, 0.068]);
      const upper = mesh(actor, cylinder, palette.white);
      const lower = mesh(actor, cylinder, palette.skin);
      const elbow = mesh(actor, smallSphere, palette.skin, null, [0.045, 0.045, 0.045]);
      const hand = makeHand();
      hand.name = side < 0 ? 'Left hand' : 'Right hand';
      if (side > 0) hand.scale.x = -1;
      actor.add(hand);
      return { side, shoulder, upper, lower, elbow, hand };
    });

    // Targets are hand-group origins, in actor-local metres.
    // Out-of-reach targets use straight links, retaining the requested hand point.
    actor.pose = (leftHandVec3, rightHandVec3) => {
      [leftHandVec3, rightHandVec3].forEach((target, index) => {
        const arm = arms[index];
        const delta = new THREE.Vector3().subVectors(target, arm.shoulder);
        const distance = Math.max(delta.length(), 0.0001);
        const direction = delta.clone().multiplyScalar(1 / distance);
        const upperLength = 0.26;
        const lowerLength = 0.25;
        let along = distance * upperLength / (upperLength + lowerLength);
        let bendDistance = 0;
        if (distance < upperLength + lowerLength && distance > 0.011) {
          along = (upperLength ** 2 - lowerLength ** 2 + distance ** 2) / (2 * distance);
          bendDistance = Math.sqrt(Math.max(0, upperLength ** 2 - along ** 2));
        }
        const bend = new THREE.Vector3(arm.side * 0.3, -0.4, 1);
        bend.addScaledVector(direction, -bend.dot(direction));
        if (bend.lengthSq() < 0.00001) bend.set(1, 0, 0);
        bend.normalize();
        const elbowPosition = arm.shoulder.clone()
          .addScaledVector(direction, along).addScaledVector(bend, bendDistance);
        link(arm.upper, arm.shoulder, elbowPosition, 0.055);
        link(arm.lower, elbowPosition, target, 0.038);
        arm.elbow.position.copy(elbowPosition);
        arm.hand.position.copy(target);
        const handDirection = new THREE.Vector3().subVectors(elbowPosition, target).normalize();
        arm.hand.quaternion.setFromUnitVectors(yAxis, handDirection);
      });
      return actor;
    };
    actor.resetPose = () => actor.pose(
      new THREE.Vector3(-0.265, 0.865, 0.025),
      new THREE.Vector3(0.265, 0.865, 0.025),
    );
    actor.userData.hands = { left: arms[0].hand, right: arms[1].hand };
    actor.resetPose();
    return actor;
  }

  function bowlGeometry(radius, height, segments) {
    const profile = [
      [0.001, 0], [0.22, 0.025], [0.5, 0.14], [0.77, 0.4],
      [0.94, 0.73], [1, 1], [0.965, 1], [0.9, 0.74],
      [0.73, 0.43], [0.46, 0.19], [0.2, 0.09], [0.001, 0.09],
    ].map(([x, y]) => new THREE.Vector2(x * radius, y * height));
    return new THREE.LatheGeometry(profile, segments);
  }

  function addFood(parent, radius, surfaceY, quantity) {
    for (let index = 0; index < quantity; index += 1) {
      const angle = index * 2.39996;
      const distance = radius * (0.31 + (index % 3) * 0.19);
      const x = Math.cos(angle) * distance;
      const z = Math.sin(angle) * distance;
      const size = radius * 0.13;
      if (index % 3 === 0) {
        mesh(parent, smallSphere, palette.meatball,
          [x, surfaceY + size * 0.35, z], [size, size, size]);
      } else if (index % 3 === 1) {
        const tofu = mesh(parent, box, palette.tofu,
          [x, surfaceY + size * 0.3, z], [size * 1.8, size * 1.1, size * 1.3]);
        tofu.rotation.y = angle;
        tofu.rotation.z = 0.16;
      } else {
        const leaf = mesh(parent, smallSphere, palette.leaf,
          [x, surfaceY + size * 0.25, z], [size * 1.15, size * 0.25, size * 2.1]);
        leaf.rotation.set(0.2, angle, 0.16);
      }
    }
  }

  const host = makeActor('Host — neutral stand-in', true);
  const staff = makeActor('Staff — neutral stand-in', false);
  const wok = new THREE.Group();
  wok.name = 'Cooking wok with demonstration food';
  mesh(wok, bowlGeometry(0.36, 0.21, 24), palette.iron);
  mesh(wok, disk, palette.broth, [0, 0.163, 0], [0.311, 0.012, 0.311]);
  const handleGeometry = new THREE.TorusGeometry(0.057, 0.012, 6, 12);
  for (const side of [-1, 1]) {
    const handle = mesh(wok, handleGeometry, palette.iron, [side * 0.386, 0.195, 0]);
    handle.rotation.x = Math.PI / 2;
    mesh(wok, box, palette.iron, [side * 0.349, 0.19, 0], [0.07, 0.022, 0.025]);
  }
  addFood(wok, 0.3, 0.174, 12);
  const ladle = new THREE.Group();
  ladle.name = 'Animated ladle';
  ladle.position.set(0.09, 0.18, 0.02);
  const scoop = mesh(ladle, bowlGeometry(0.055, 0.024, 12), palette.steel);
  scoop.position.y = -0.01;
  const ladleStart = new THREE.Vector3(0, 0.008, 0.03);
  const ladleEnd = new THREE.Vector3(0, 0.29, 0.36);
  link(mesh(ladle, cylinder, palette.steel), ladleStart, ladleEnd, 0.008);
  link(mesh(ladle, cylinder, palette.dark),
    new THREE.Vector3(0, 0.26, 0.323), new THREE.Vector3(0, 0.36, 0.44), 0.015);
  wok.add(ladle);
  wok.userData.ladle = ladle;

  const steam = [];
  for (let index = 0; index < 7; index += 1) {
    const material = new THREE.MeshBasicMaterial({
      color: 0xfff9ef, transparent: true, opacity: 0.12,
      depthWrite: false, toneMapped: false,
    });
    const puff = mesh(wok, smallSphere, material);
    puff.castShadow = false;
    puff.receiveShadow = false;
    puff.renderOrder = 2;
    steam.push(puff);
  }
  function updateSteam(t) {
    if (!wok.visible) return;
    steam.forEach((puff, index) => {
      const phase = ((t * 0.23 + index / steam.length) % 1 + 1) % 1;
      const angle = index * 2.39996;
      puff.position.set(
        Math.cos(angle) * 0.13 + Math.sin(t * 0.8 + index) * phase * 0.055,
        0.2 + phase * 0.55,
        Math.sin(angle) * 0.12 + Math.cos(t * 0.6 + index) * phase * 0.04,
      );
      const size = 0.023 + phase * 0.045;
      puff.scale.set(size, size * 1.8, size);
      puff.material.opacity = 0.15 * Math.sin(Math.PI * phase);
    });
  }
  updateSteam(0);

  const foodBowl = new THREE.Group();
  foodBowl.name = 'Brass food bowl';
  mesh(foodBowl, bowlGeometry(0.13, 0.08, 20), palette.brass);
  mesh(foodBowl, disk, palette.broth, [0, 0.061, 0], [0.111, 0.006, 0.111]);
  addFood(foodBowl, 0.105, 0.067, 7);

  // Simple vector lettering keeps this module independent of DOM/canvas/font assets.
  function demoLabel(parent, width, y, z, material) {
    const glyphs = {
      D: [[0, 0, 0, 1], [0, 1, 0.65, 1], [0.65, 1, 0.85, 0.8],
        [0.85, 0.8, 0.85, 0.2], [0.85, 0.2, 0.65, 0], [0.65, 0, 0, 0]],
      E: [[0, 0, 0, 1], [0, 1, 0.85, 1], [0, 0.5, 0.65, 0.5], [0, 0, 0.85, 0]],
      M: [[0, 0, 0, 1], [0, 1, 0.43, 0.42], [0.43, 0.42, 0.85, 1], [0.85, 1, 0.85, 0]],
      O: [[0, 0, 0, 1], [0, 1, 0.85, 1], [0.85, 1, 0.85, 0], [0.85, 0, 0, 0]],
    };
    const unit = width / 4.45;
    Array.from('DEMO').forEach((letter, index) => {
      for (const [x1, y1, x2, y2] of glyphs[letter]) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const stroke = mesh(parent, box, material,
          [-width / 2 + (index * 1.2 + (x1 + x2) / 2) * unit,
            y + ((y1 + y2) / 2 - 0.5) * unit, z],
          [Math.hypot(dx, dy) * unit + 0.0003, unit * 0.11, 0.0004]);
        stroke.rotation.z = Math.atan2(dy, dx);
        stroke.castShadow = false;
      }
    });
  }
  const phone = new THREE.Group();
  phone.name = 'Phone — DEMO screen';
  mesh(phone, box, palette.dark, [0, 0, 0], [0.075, 0.15, 0.012]);
  mesh(phone, box, palette.screen, [0, 0.002, 0.0063], [0.065, 0.128, 0.0008]);
  demoLabel(phone, 0.052, 0.014, 0.007, palette.ink);
  mesh(phone, box, palette.ink, [0, -0.043, 0.007], [0.028, 0.003, 0.0004]);
  mesh(phone, box, palette.dark, [0, 0.064, 0.007], [0.018, 0.003, 0.0004]);

  const ticket = new THREE.Group();
  ticket.name = 'Blank demonstration ticket';
  mesh(ticket, box, palette.white, [0, 0, 0], [0.07, 0.13, 0.0008]);
  demoLabel(ticket, 0.045, 0.041, 0.0007, palette.burgundy);
  for (let index = 0; index < 4; index += 1) {
    mesh(ticket, box, palette.guide,
      [-0.004, 0.013 - index * 0.017, 0.0007], [0.042, 0.0015, 0.0003]);
  }

  const scanner = new THREE.Group();
  scanner.name = 'Handheld scanner stand-in';
  const grip = mesh(scanner, box, palette.gray, [0, -0.055, 0], [0.034, 0.11, 0.039]);
  grip.rotation.x = -0.22;
  mesh(scanner, box, palette.dark, [0, 0.012, 0.026], [0.065, 0.055, 0.11]);
  mesh(scanner, box, palette.screen, [0, 0.014, 0.082], [0.051, 0.035, 0.002]);
  mesh(scanner, box, palette.red, [0, 0.014, 0.0835], [0.037, 0.002, 0.0005]);
  mesh(scanner, box, palette.burgundy, [0, -0.022, 0.03], [0.023, 0.017, 0.012]);

  scene.add(host, staff, wok, foodBowl, phone, ticket, scanner);
  return {
    actors: { host, staff },
    wok,
    foodBowl,
    phone,
    ticket,
    scanner,
    updateSteam,
    makeHand,
  };
}
