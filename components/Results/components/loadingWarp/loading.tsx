import { useEffect, useRef } from "react";

import styles from "./styles.module.css";

const CONFIG = {
  bn: 5,
  hl: 1,
  hu: 359,
  sl: 1,
  su: 4,
  dl: 0,
  du: 5,
  cell: 5,
  depth: 100,
} as const;

const randomFromRange = (from: number, to: number): number => {
  // ToDo: make this function((
  // console.log(Math.floor(Math.random() * 100));
  // const temp = new Array(to - from).fill(0);
  // console.log(Math.random().toString().slice(2).slice(-2));
  return 0;
};

const Loading = () => {
  const topRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const leftRef = useRef<HTMLDivElement>(null);

  const SIDES = [topRef, rightRef, bottomRef, leftRef] as const;

  useEffect(() => {
    // randomFromRange(0, 0);

    let hue = 0,
      x = 0,
      speed = 0,
      delay = 0,
      ar = 0;

    for (const SIDE of SIDES) {
      if (SIDE.current) {
        SIDE.current.innerHTML = "";
        const NUMBER = 4;
        const BEAMS = new Array(NUMBER).fill({}).map((beam) => {
          hue += 1;
          x += 1;
          speed += 1;
          delay += 1;

          if (hue === CONFIG.hu) {
            hue = CONFIG.hl;
          }
          if (x === 100 / CONFIG.cell - 1) {
            x = 0;
          }
          if (speed === CONFIG.su) {
            speed = CONFIG.sl;
          }
          if (delay === CONFIG.du) {
            delay = CONFIG.dl;
          }

          return {
            hue,
            x,
            speed,
            delay,
          };
          // return {
          //   hue: gsap.utils.random(CONFIG.hl, CONFIG.hu, 1),
          //   x: gsap.utils.random(0, 100 / CONFIG.cell - 1, 1),
          //   speed: gsap.utils.random(CONFIG.sl, CONFIG.su),
          //   delay: gsap.utils.random(CONFIG.dl, CONFIG.du),
          // };
        });

        for (const BEAM of BEAMS) {
          ar += 1;
          if (ar === 10) {
            ar = 1;
          }

          SIDE.current.appendChild(
            Object.assign(document.createElement("div"), {
              className: `animate-warp  ${styles.beam}`,
              style: `
          --hue: ${BEAM.hue};
          --ar: ${ar};
          --x: ${BEAM.x};
          --speed: ${BEAM.speed};
          --delay: ${BEAM.delay};
        `,
            }),
          );
        }
      }
    }
  }, []);

  return (
    <div className="relative h-full w-full">
      <article className={`bg-gray-800 text-gray-100 ${styles.article}`}>
        <h2>
          Одно мгновение...
          <br />
          <br />
          Собираем твою статистику
          <br />
          за 2023 год!
        </h2>
      </article>
      <div className={`${styles.warp}`}>
        <div
          ref={topRef}
          className={`${styles.warp__side} ${styles.warp__side__top}`}
        ></div>
        <div
          ref={rightRef}
          className={`${styles.warp__side} ${styles.warp__side__right}`}
        ></div>
        <div
          ref={bottomRef}
          className={`${styles.warp__side} ${styles.warp__side__bottom}`}
        ></div>
        <div
          ref={leftRef}
          className={`${styles.warp__side} ${styles.warp__side__left}`}
        ></div>
      </div>
    </div>
  );
};

export default Loading;
