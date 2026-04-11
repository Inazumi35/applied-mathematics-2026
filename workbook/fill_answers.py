#!/usr/bin/env python3
"""
applied_math_problems.yaml の answer フィールドに解答を一括入力するスクリプト。
実行後、元ファイルを上書きする。
"""

import yaml
import os
import copy

# ============================================================
# 解答データ（問題番号 → 解答テキスト）
# リスト型は小問ごとの解答
# ============================================================

ANSWERS = {
    # ============================
    # 2章 ラプラス変換 — Basic
    # ============================
    74: r"$\mathcal{L}[t^3] = \dfrac{3!}{s^4} = \dfrac{6}{s^4} \quad (s>0)$",

    75: r"$\mathcal{L}[3t^2+2] = 3\cdot\dfrac{2!}{s^3} + \dfrac{2}{s} = \dfrac{6}{s^3} + \dfrac{2s^2}{s^3} = \dfrac{2(s^2+3)}{s^3} \quad (s>0)$",

    76: r"$\mathcal{L}[e^t - e^{-2t}] = \dfrac{1}{s-1} - \dfrac{1}{s+2} = \dfrac{(s+2)-(s-1)}{(s-1)(s+2)} = \dfrac{3}{(s-1)(s+2)} \quad (s>1)$",

    77: (
        r"$\mathcal{L}[\sin 3t] = \displaystyle\int_0^\infty e^{-st}\sin 3t\,dt$"
        "\n\n"
        r"部分積分を2回行うと，$\mathcal{L}[\sin 3t] = \dfrac{3}{s^2+9} \quad (s>0)$"
    ),

    78: r"$\mathcal{L}[\cosh 2t] = \mathcal{L}\!\left[\dfrac{e^{2t}+e^{-2t}}{2}\right] = \dfrac{1}{2}\!\left(\dfrac{1}{s-2}+\dfrac{1}{s+2}\right) = \dfrac{s}{s^2-4} \quad (s>2)$",

    79: [
        r"グラフ：$t=3$ で 0 から 1 に跳ぶステップ関数．$\mathcal{L}[U(t-3)] = \dfrac{e^{-3s}}{s} \quad (s>0)$",
        r"グラフ：$t=2$ で 0 から 3 に跳ぶ．$\mathcal{L}[3U(t-2)] = \dfrac{3e^{-2s}}{s} \quad (s>0)$",
    ],

    80: [
        r"$f(t) = U(t-1) - U(t-3)$．$\mathcal{L}[f(t)] = \dfrac{e^{-s} - e^{-3s}}{s} \quad (s>0)$",
        r"$f(t) = 2U(t-1)$．$\mathcal{L}[f(t)] = \dfrac{2e^{-s}}{s} \quad (s>0)$",
    ],

    81: (
        r"$\mathcal{L}[\cosh t] = \dfrac{s}{s^2-1}$ において $t$ を $\omega t$ に置き換え，"
        r"相似性より $\mathcal{L}[\cosh \omega t] = \dfrac{1}{\omega}\cdot\dfrac{s/\omega}{(s/\omega)^2-1} = \dfrac{s}{s^2-\omega^2}$"
    ),

    82: (
        r"$\sin t\cos t = \dfrac{1}{2}\sin 2t$ より，"
        r"$\mathcal{L}[\sin t\cos t] = \dfrac{1}{2}\cdot\dfrac{2}{s^2+4} = \dfrac{1}{s^2+4}$"
    ),

    83: (
        r"第1移動法則 $\mathcal{L}[t^n e^{at}] = \dfrac{n!}{(s-a)^{n+1}}$ より，"
        r"$\mathcal{L}[t^3 e^{2t}] = \dfrac{3!}{(s-2)^4} = \dfrac{6}{(s-2)^4}$"
    ),

    84: (
        r"第2移動法則 $\mathcal{L}[f(t-a)U(t-a)] = e^{-as}F(s)$ より，"
        r"$\mathcal{L}\!\left[\cos\!\left(t-\dfrac{\pi}{6}\right)U\!\left(t-\dfrac{\pi}{6}\right)\right] = \dfrac{se^{-\pi s/6}}{s^2+1}$"
    ),

    85: (
        r"グラフ：$t \geq 1$ で傾き 1 の直線（$t<1$ で $0$）．"
        "\n\n"
        r"$\mathcal{L}[(t-1)U(t-1)] = \dfrac{e^{-s}}{s^2}$"
    ),

    86: (
        r"像関数の微分法則 $\mathcal{L}[tf(t)] = -F'(s)$ を用いる．"
        "\n\n"
        r"$\mathcal{L}[\sinh t] = \dfrac{1}{s^2-1}$ より $\mathcal{L}[t\sinh t] = -\dfrac{d}{ds}\dfrac{1}{s^2-1} = \dfrac{2s}{(s^2-1)^2}$"
        "\n\n"
        r"$\mathcal{L}[\cosh t] = \dfrac{s}{s^2-1}$ より $\mathcal{L}[t\cosh t] = -\dfrac{d}{ds}\dfrac{s}{s^2-1} = \dfrac{s^2+1}{(s^2-1)^2}$"
    ),

    87: (
        r"両辺をラプラス変換し，$f(0)=0$ を用いると"
        "\n"
        r"$sF(s) + 4F(s) = \dfrac{2}{s^3}$"
        "\n\n"
        r"よって $F(s) = \mathcal{L}[f(t)] = \dfrac{2}{s^3(s+4)}$"
    ),

    88: (
        r"$\mathcal{L}[e^{3t}] = \dfrac{1}{s-3}$ の $n$ 階微分法則より"
        "\n\n"
        r"$\mathcal{L}[t^n e^{3t}] = (-1)^n \dfrac{d^n}{ds^n}\dfrac{1}{s-3} = \dfrac{n!}{(s-3)^{n+1}}$"
    ),

    89: (
        r"像関数の積分法則 $\mathcal{L}\!\left[\dfrac{f(t)}{t}\right] = \displaystyle\int_s^\infty F(u)\,du$ を用いる．"
        "\n\n"
        r"$F(s) = \dfrac{1}{s-3} - \dfrac{1}{s+1}$ より"
        "\n"
        r"$\displaystyle\int_s^\infty \!\left(\dfrac{1}{u-3}-\dfrac{1}{u+1}\right)du = \left[\ln\dfrac{u-3}{u+1}\right]_s^\infty = -\ln\dfrac{s-3}{s+1} = \ln\dfrac{s+1}{s-3}$"
    ),

    90: [
        r"$\dfrac{1}{(s+2)^2}$ より $\mathcal{L}^{-1} = te^{-2t}$",
        r"$\dfrac{1}{(s-1)(s-3)} = \dfrac{1}{2}\!\left(\dfrac{1}{s-3}-\dfrac{1}{s-1}\right)$ より $\mathcal{L}^{-1} = \dfrac{1}{2}(e^{3t}-e^t)$",
        r"$\dfrac{1}{(s-3)^2+1}$ より $\mathcal{L}^{-1} = e^{3t}\sin t$",
    ],

    91: [
        (
            r"$\dfrac{s+1}{(s+3)^2} = \dfrac{(s+3)-2}{(s+3)^2} = \dfrac{1}{s+3} - \dfrac{2}{(s+3)^2}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = e^{-3t} - 2te^{-3t}$"
        ),
        (
            r"$\dfrac{s}{(s-2)^2+9} = \dfrac{(s-2)+2}{(s-2)^2+9}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = e^{2t}\cos 3t + \dfrac{2}{3}e^{2t}\sin 3t$"
        ),
    ],

    92: [
        (
            r"部分分数分解：$\dfrac{2s^2-5s-6}{(s+2)(s-1)(s-2)} = \dfrac{A}{s+2}+\dfrac{B}{s-1}+\dfrac{C}{s-2}$"
            "\n\n"
            r"$A=\dfrac{8+10-6}{(-3)(-4)}=1$，$B=\dfrac{2-5-6}{(3)(-1)}=3$，$C=\dfrac{8-10-6}{(4)(1)}=-2$"
            "\n\n"
            r"$\mathcal{L}^{-1} = e^{-2t}+3e^t-2e^{2t}$"
        ),
        (
            r"$\dfrac{1}{s^2(s+1)} = \dfrac{A}{s}+\dfrac{B}{s^2}+\dfrac{C}{s+1}$"
            "\n\n"
            r"$A=-1$，$B=1$，$C=1$ より $\mathcal{L}^{-1} = -1+t+e^{-t}$"
        ),
    ],

    # ============================
    # 2章 ラプラス変換 — Check
    # ============================
    93: [
        r"$\mathcal{L}[4t^2-3t+2] = \dfrac{8}{s^3}-\dfrac{3}{s^2}+\dfrac{2}{s}$",
        r"$(t-1)^3 = t^3-3t^2+3t-1$ より $\mathcal{L} = \dfrac{6}{s^4}-\dfrac{6}{s^3}+\dfrac{3}{s^2}-\dfrac{1}{s}$",
        r"$\mathcal{L}[4e^{3t}-3e^{2t}] = \dfrac{4}{s-3}-\dfrac{3}{s-2}$",
        r"$e^{3t+2}=e^2 e^{3t}$ より $\mathcal{L} = \dfrac{e^2}{s-3}$",
    ],

    94: (
        r"$\mathcal{L}[te^{\alpha t}] = \displaystyle\int_0^\infty te^{\alpha t}e^{-st}\,dt = \int_0^\infty te^{-(s-\alpha)t}\,dt$"
        "\n\n"
        r"部分積分より $= \dfrac{1}{(s-\alpha)^2} \quad (s>\alpha)$"
    ),

    95: (
        r"$\mathcal{L}[\sinh \omega t] = \dfrac{1}{2}\!\left(\dfrac{1}{s-\omega}-\dfrac{1}{s+\omega}\right) = \dfrac{\omega}{s^2-\omega^2}$"
    ),

    96: [
        (
            r"$f(t) = 1 - U(t-2) + U(t-3)$"
            "\n\n"
            r"$\mathcal{L}[f(t)] = \dfrac{1}{s} - \dfrac{e^{-2s}}{s} + \dfrac{e^{-3s}}{s}$"
        ),
        (
            r"$f(t) = 1 - U(t-1) + 2U(t-3)$"
            "\n"
            r"$= 1 - U(t-1) + 2U(t-3)$"
            "\n\n"
            r"$\mathcal{L}[f(t)] = \dfrac{1}{s} - \dfrac{e^{-s}}{s} + \dfrac{2e^{-3s}}{s}$"
        ),
    ],

    97: [
        r"$\mathcal{L}[te^{3t}] = \dfrac{1}{(s-3)^2}$",
        r"$\mathcal{L}[t^2 e^{-2t}] = \dfrac{2}{(s+2)^3}$",
        r"$\mathcal{L}[e^{2t}\sin 3t] = \dfrac{3}{(s-2)^2+9}$",
        r"$\mathcal{L}[e^{-t}\cos 2t] = \dfrac{s+1}{(s+1)^2+4}$",
    ],

    98: (
        r"グラフ：$t \geq 2$ で放物線 $(t-2)^2$（$t<2$ で $0$）．"
        "\n\n"
        r"$\mathcal{L}[(t-2)^2 U(t-2)] = \dfrac{2e^{-2s}}{s^3}$"
    ),

    99: (
        r"$\mathcal{L}[\sinh \omega t] = \dfrac{\omega}{s^2-\omega^2}$ の微分法則より"
        "\n\n"
        r"$\mathcal{L}[t\sinh \omega t] = -\dfrac{d}{ds}\dfrac{\omega}{s^2-\omega^2} = \dfrac{2\omega s}{(s^2-\omega^2)^2}$"
        "\n\n"
        r"$\mathcal{L}[t\cosh \omega t] = -\dfrac{d}{ds}\dfrac{s}{s^2-\omega^2} = \dfrac{s^2+\omega^2}{(s^2-\omega^2)^2}$"
    ),

    100: (
        r"$f'(t)+3f(t)=\sin t$，$f(0)=1$ をラプラス変換すると"
        "\n"
        r"$sF(s)-1+3F(s) = \dfrac{1}{s^2+1}$"
        "\n\n"
        r"$(s+3)F(s) = 1+\dfrac{1}{s^2+1} = \dfrac{s^2+2}{s^2+1}$"
        "\n\n"
        r"$\mathcal{L}[f(t)] = F(s) = \dfrac{s^2+2}{(s+3)(s^2+1)}$"
    ),

    101: (
        r"$\mathcal{L}[\cos t] = \dfrac{s}{s^2+1}$ の2階微分法則より"
        "\n\n"
        r"$\mathcal{L}[t^2\cos t] = \dfrac{d^2}{ds^2}\dfrac{s}{s^2+1} = \dfrac{2s(s^2-3)}{(s^2+1)^3}$"
    ),

    102: [
        r"$\dfrac{1}{(s-2)^4}$ より $\mathcal{L}^{-1} = \dfrac{1}{6}t^3 e^{2t}$",
        (
            r"$\dfrac{s+2}{(s-1)^2} = \dfrac{1}{s-1}+\dfrac{3}{(s-1)^2}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = e^t + 3te^t$"
        ),
        (
            r"$\dfrac{s}{(s-3)(s+2)} = \dfrac{3}{5}\cdot\dfrac{1}{s-3}+\dfrac{2}{5}\cdot\dfrac{1}{s+2}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = \dfrac{3}{5}e^{3t}+\dfrac{2}{5}e^{-2t}$"
        ),
        r"$\dfrac{2s+3}{s^2+4} = 2\cdot\dfrac{s}{s^2+4}+\dfrac{3}{2}\cdot\dfrac{2}{s^2+4}$ より $\mathcal{L}^{-1} = 2\cos 2t+\dfrac{3}{2}\sin 2t$",
        (
            r"$\dfrac{2s+1}{(s+1)^2+4} = \dfrac{2(s+1)-1}{(s+1)^2+4}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = 2e^{-t}\cos 2t - \dfrac{1}{2}e^{-t}\sin 2t$"
        ),
    ],

    103: [
        (
            r"部分分数分解：$\dfrac{s-5}{(s+1)(s-2)(s-3)} = \dfrac{A}{s+1}+\dfrac{B}{s-2}+\dfrac{C}{s-3}$"
            "\n\n"
            r"$A=\dfrac{-6}{(-3)(-4)}=-\dfrac{1}{2}$，$B=\dfrac{-3}{(3)(-1)}=1$，$C=\dfrac{-2}{(4)(1)}=-\dfrac{1}{2}$"
            "\n\n"
            r"$\mathcal{L}^{-1} = -\dfrac{1}{2}e^{-t}+e^{2t}-\dfrac{1}{2}e^{3t}$"
        ),
        (
            r"$\dfrac{2s^2+7}{(s-2)^2(s+3)} = \dfrac{A}{s-2}+\dfrac{B}{(s-2)^2}+\dfrac{C}{s+3}$"
            "\n\n"
            r"$B=3$，$C=1$，$A=1$"
            "\n\n"
            r"$\mathcal{L}^{-1} = e^{2t}+3te^{2t}+e^{-3t}$"
        ),
    ],

    106: [
        (
            r"$sX-1-X = \dfrac{1}{s-2}$ より $(s-1)X = 1+\dfrac{1}{s-2} = \dfrac{s-1}{s-2}$"
            "\n\n"
            r"$X = \dfrac{1}{s-2}$ より $x(t) = e^{2t}$"
        ),
        (
            r"$sX+X = \dfrac{1}{s}$ より $X = \dfrac{1}{s(s+1)} = \dfrac{1}{s}-\dfrac{1}{s+1}$"
            "\n\n"
            r"$x(t) = 1-e^{-t}$"
        ),
    ],

    107: [
        (
            r"$s^2X-sX-2X = \dfrac{1}{s-1}$，$(s^2-s-2)X = \dfrac{1}{s-1}$"
            "\n\n"
            r"$X = \dfrac{1}{(s-1)(s-2)(s+1)} = -\dfrac{1}{2}\cdot\dfrac{1}{s-1}+\dfrac{1}{3}\cdot\dfrac{1}{s-2}+\dfrac{1}{6}\cdot\dfrac{1}{s+1}$"
            "\n\n"
            r"$x(t) = \dfrac{1}{6}e^{-t}-\dfrac{1}{2}e^t+\dfrac{1}{3}e^{2t}$"
        ),
        (
            r"$(s^2-2s+5)X = 1$，$X = \dfrac{1}{(s-1)^2+4}$"
            "\n\n"
            r"$x(t) = \dfrac{1}{2}e^t\sin 2t$"
        ),
    ],

    108: [
        (
            r"$(s^2-2s)X = s-2$（$x(0)=1$，$x'(0)=c$ とする）"
            "\n"
            r"$x(1)=e^2$ の条件から $c=2$．$X = \dfrac{s+c-2}{s(s-2)}$"
            "\n\n"
            r"$c=2$ のとき $X = \dfrac{1}{s-2}$ より $x(t) = e^{2t}$"
        ),
        (
            r"$x(0)=1$，$x(\pi/6)=0$ の条件で解くと"
            "\n"
            r"$(s^2+9)X = s+c+\dfrac{3}{s}$"
            "\n\n"
            r"$x(t) = \cos 3t + \dfrac{c}{3}\sin 3t + \dfrac{1}{3}(1-\cos 3t)$"
            "\n"
            r"$x(\pi/6)=0$ より $c=-1$．$x(t) = \dfrac{1}{3}+\dfrac{2}{3}\cos 3t-\dfrac{1}{3}\sin 3t$"
        ),
    ],

    109: [
        (
            r"$x(0)=c_1$ として $(s+4)X = c_1+\dfrac{1}{s}$"
            "\n\n"
            r"$X = \dfrac{c_1}{s+4}+\dfrac{1}{s(s+4)}$ より $x(t) = c_1 e^{-4t}+\dfrac{1}{4}(1-e^{-4t})$"
            "\n\n"
            r"一般解：$x(t) = Ce^{-4t}+\dfrac{1}{4}$"
        ),
        (
            r"$(s^2-9)X = sc_1+c_2$"
            "\n\n"
            r"一般解：$x(t) = C_1 e^{3t}+C_2 e^{-3t}$"
        ),
        (
            r"$(s^2+16)X = sc_1+c_2+\dfrac{1}{s^2}$"
            "\n\n"
            r"一般解：$x(t) = C_1\cos 4t+C_2\sin 4t+\dfrac{t}{16}$"
        ),
    ],

    110: (
        r"$t^3 * t = \displaystyle\int_0^t \tau^3(t-\tau)\,d\tau = \int_0^t (t\tau^3-\tau^4)\,d\tau = \dfrac{t^5}{4}-\dfrac{t^5}{5} = \dfrac{t^5}{20}$"
    ),

    111: (
        r"$t*(t^3+t^4) = t*t^3 + t*t^4 = \dfrac{t^5}{20} + \displaystyle\int_0^t \tau(t-\tau)^4\,d\tau$"
        "\n\n"
        r"$t*t^4 = \displaystyle\int_0^t \tau^4(t-\tau)\,d\tau = \dfrac{t^6}{5}-\dfrac{t^6}{6} = \dfrac{t^6}{30}$"
        "\n\n"
        r"よって $t*(t^3+t^4) = \dfrac{t^5}{20}+\dfrac{t^6}{30}$"
    ),

    112: (
        r"$\mathcal{L}[t^3*t] = \mathcal{L}[t^3]\cdot\mathcal{L}[t] = \dfrac{6}{s^4}\cdot\dfrac{1}{s^2} = \dfrac{6}{s^6}$"
        "\n\n"
        r"直接計算：$\mathcal{L}\!\left[\dfrac{t^5}{20}\right] = \dfrac{1}{20}\cdot\dfrac{5!}{s^6} = \dfrac{6}{s^6}$（一致）"
    ),

    113: [
        (
            r"$\mathcal{L}^{-1}\!\left[\dfrac{F(s)}{(s+2)^2}\right] = f(t) * te^{-2t}$"
        ),
        (
            r"$\dfrac{1}{s^2-7s+12} = \dfrac{1}{(s-3)(s-4)} = \dfrac{1}{s-4}-\dfrac{1}{s-3}$"
            "\n\n"
            r"$\mathcal{L}^{-1}\!\left[\dfrac{F(s)}{s^2-7s+12}\right] = f(t) * (e^{4t}-e^{3t})$"
        ),
        (
            r"$\dfrac{1}{(s-2)^2+9}$ の逆変換は $\dfrac{1}{3}e^{2t}\sin 3t$"
            "\n\n"
            r"$\mathcal{L}^{-1}\!\left[\dfrac{F(s)}{s^2-4s+13}\right] = f(t) * \dfrac{1}{3}e^{2t}\sin 3t$"
        ),
    ],

    114: [
        (
            r"$X(s)\cdot\dfrac{s}{s^2+1} = \dfrac{2}{s^3}$ より $X(s) = \dfrac{2(s^2+1)}{s^4}$"
            "\n\n"
            r"$= \dfrac{2}{s^2}+\dfrac{2}{s^4}$ より $x(t) = 2t+\dfrac{t^3}{3}$"
        ),
        (
            r"$X(s)\cdot\dfrac{1}{s-2} = \dfrac{3}{s^2+9}$ より $X(s) = \dfrac{3(s-2)}{s^2+9}$"
            "\n\n"
            r"$= \dfrac{3s}{s^2+9}-\dfrac{6}{s^2+9}$ より $x(t) = 3\cos 3t-2\sin 3t$"
        ),
    ],

    115: (
        r"$Y(s)(s^2-4s+3) = X(s)$ より伝達関数 $G(s) = \dfrac{Y(s)}{X(s)} = \dfrac{1}{s^2-4s+3} = \dfrac{1}{(s-1)(s-3)}$"
        "\n\n"
        r"$g(t) = \mathcal{L}^{-1}[G(s)] = \dfrac{1}{2}(e^{3t}-e^t)$"
        "\n\n"
        r"$y(t) = g(t)*x(t) = \dfrac{1}{2}\displaystyle\int_0^t (e^{3(t-\tau)}-e^{t-\tau})x(\tau)\,d\tau$"
    ),

    116: (
        r"たたみ込み $e^{2t}*\delta(t) = e^{2t}$ より"
        "\n"
        r"$\mathcal{L}[e^{2t}*\delta(t)] = \mathcal{L}[e^{2t}] = \dfrac{1}{s-2}$"
        "\n\n"
        r"（別解）$\mathcal{L}[e^{2t}]\cdot\mathcal{L}[\delta(t)] = \dfrac{1}{s-2}\cdot 1 = \dfrac{1}{s-2}$"
    ),

    117: (
        r"$(s^2+2s+1)Y = 1$ より $Y = \dfrac{1}{(s+1)^2}$"
        "\n\n"
        r"$y(t) = te^{-t}$"
    ),

    118: [
        (
            r"$(s-1)X = 1+\dfrac{1}{(s-1)^2}$ より $X = \dfrac{1}{s-1}+\dfrac{1}{(s-1)^3}$"
            "\n\n"
            r"$x(t) = e^t + \dfrac{1}{2}t^2 e^t$"
        ),
        (
            r"$(s^2+4)X = s+2+\dfrac{1}{s^2}$"
            "\n\n"
            r"$X = \dfrac{s}{s^2+4}+\dfrac{2}{s^2+4}+\dfrac{1}{s^2(s^2+4)}$"
            "\n\n"
            r"$\dfrac{1}{s^2(s^2+4)} = \dfrac{1}{4}\!\left(\dfrac{1}{s^2}-\dfrac{1}{s^2+4}\right)$"
            "\n\n"
            r"$x(t) = \cos 2t + \sin 2t + \dfrac{1}{4}t - \dfrac{1}{8}\sin 2t = \cos 2t + \dfrac{7}{8}\sin 2t + \dfrac{t}{4}$"
        ),
        (
            r"$(s^2-5s+6)X = s-5+\dfrac{1}{s-3}$，$(s-2)(s-3)X = s-5+\dfrac{1}{s-3}$"
            "\n\n"
            r"$X = \dfrac{s-5}{(s-2)(s-3)}+\dfrac{1}{(s-3)^2(s-2)}$"
            "\n\n"
            r"部分分数分解して $x(t) = -3e^{2t}+4e^{3t}+te^{3t}-e^{2t}+e^{3t}$"
            "\n"
            r"整理して $x(t) = -4e^{2t}+5e^{3t}+te^{3t}$"
        ),
    ],

    119: [
        (
            r"$(s^2+9)X = s+1+\dfrac{s}{s^2+1}$"
            "\n\n"
            r"$X = \dfrac{s+1}{s^2+9}+\dfrac{s}{(s^2+1)(s^2+9)}$"
            "\n\n"
            r"$\dfrac{s}{(s^2+1)(s^2+9)} = \dfrac{1}{8}\!\left(\dfrac{s}{s^2+1}-\dfrac{s}{s^2+9}\right)$"
            "\n\n"
            r"$x(t) = \cos 3t+\dfrac{1}{3}\sin 3t+\dfrac{1}{8}\cos t-\dfrac{1}{8}\cos 3t$"
            "\n"
            r"$= \dfrac{7}{8}\cos 3t+\dfrac{1}{3}\sin 3t+\dfrac{1}{8}\cos t$"
        ),
        (
            r"一般解 $x(t) = C_1\cos 3t + C_2\sin 3t + \dfrac{1}{8}\cos t$ に $x(0)=1$ を代入すると $C_1 = \dfrac{7}{8}$"
            "\n\n"
            r"$x\!\left(\dfrac{\pi}{4}\right) = \dfrac{7}{8}\cos\dfrac{3\pi}{4}+C_2\sin\dfrac{3\pi}{4}+\dfrac{1}{8}\cos\dfrac{\pi}{4} = 0$"
            "\n\n"
            r"$-\dfrac{7\sqrt{2}}{16}+\dfrac{\sqrt{2}}{2}C_2+\dfrac{\sqrt{2}}{16} = 0$ より $C_2 = \dfrac{3}{4}$"
            "\n\n"
            r"$x(t) = \dfrac{7}{8}\cos 3t+\dfrac{3}{4}\sin 3t+\dfrac{1}{8}\cos t$"
        ),
        (
            r"一般解：$x(t) = C_1\cos 3t + C_2\sin 3t + \dfrac{1}{8}\cos t$"
        ),
    ],

    120: [
        (
            r"$(s^2+2s+5)X = s+4$ より $X = \dfrac{s+4}{(s+1)^2+4} = \dfrac{(s+1)+3}{(s+1)^2+4}$"
            "\n\n"
            r"$x(t) = e^{-t}\cos 2t + \dfrac{3}{2}e^{-t}\sin 2t$"
        ),
        (
            r"一般解 $x(t) = e^{-t}(C_1\cos 2t + C_2\sin 2t)$ に $x(0)=1$ を代入すると $C_1 = 1$"
            "\n\n"
            r"$x\!\left(\dfrac{\pi}{4}\right) = e^{-\pi/4}(1\cdot\cos\dfrac{\pi}{2}+C_2\sin\dfrac{\pi}{2}) = e^{-\pi/4}C_2 = 0$ より $C_2 = 0$"
            "\n\n"
            r"$x(t) = e^{-t}\cos 2t$"
        ),
        (
            r"一般解：$x(t) = e^{-t}(C_1\cos 2t + C_2\sin 2t)$"
        ),
    ],

    121: [
        (
            r"$\cos t * \cos t = \displaystyle\int_0^t \cos\tau\cos(t-\tau)\,d\tau$"
            "\n\n"
            r"積和公式 $\cos\tau\cos(t-\tau)=\dfrac{1}{2}[\cos t+\cos(2\tau-t)]$ を用いて"
            "\n"
            r"$= \dfrac{1}{2}t\cos t + \dfrac{1}{2}\sin t$"
        ),
        (
            r"$t * e^{2t} = \displaystyle\int_0^t \tau e^{2(t-\tau)}\,d\tau = e^{2t}\int_0^t \tau e^{-2\tau}\,d\tau$"
            "\n\n"
            r"$= \dfrac{1}{4}(e^{2t}-2t-1)$"
        ),
        (
            r"$\mathcal{L}[t^2*\sin t] = \dfrac{2}{s^3}\cdot\dfrac{1}{s^2+1} = \dfrac{2}{s^3(s^2+1)}$"
            "\n\n"
            r"部分分数分解：$\dfrac{2}{s^3(s^2+1)} = -\dfrac{2}{s}+\dfrac{2}{s^3}+\dfrac{2s}{s^2+1}$"
            "\n\n"
            r"$t^2 * \sin t = -2 + t^2 + 2\cos t$"
        ),
    ],

    122: [
        (
            r"たたみ込みのラプラス変換：$X(s)\cdot\dfrac{2}{s^2+4} = \mathcal{L}[t\sin 2t] = \dfrac{4s}{(s^2+4)^2}$"
            "\n\n"
            r"$X(s) = \dfrac{4s}{(s^2+4)^2}\cdot\dfrac{s^2+4}{2} = \dfrac{2s}{s^2+4}$"
            "\n\n"
            r"$x(t) = 2\cos 2t$"
        ),
        (
            r"$X(s) - 2X(s)\cdot\dfrac{s}{s^2+1} = \dfrac{1}{s^2+1}$"
            "\n\n"
            r"$X(s)\!\left(1-\dfrac{2s}{s^2+1}\right) = \dfrac{1}{s^2+1}$"
            "\n\n"
            r"$X(s) = \dfrac{1}{(s-1)^2}$ より $x(t) = te^t$"
        ),
        (
            r"$sX+2X+4X\cdot\dfrac{1}{s-2} = \dfrac{2}{s^3}$"
            "\n\n"
            r"$X\!\left(s+2+\dfrac{4}{s-2}\right) = \dfrac{2}{s^3}$，$X\cdot\dfrac{s^2}{s-2} = \dfrac{2}{s^3}$"
            "\n\n"
            r"$X = \dfrac{2(s-2)}{s^5} = \dfrac{2}{s^4}-\dfrac{4}{s^5}$"
            "\n\n"
            r"$x(t) = \dfrac{t^3}{3}-\dfrac{t^4}{6}$"
        ),
    ],

    123: (
        r"$(s^2+4)Y = X$ より $G(s) = \dfrac{1}{s^2+4}$"
        "\n\n"
        r"$g(t) = \dfrac{1}{2}\sin 2t$"
        "\n\n"
        r"$y(t) = \dfrac{1}{2}\displaystyle\int_0^t x(\tau)\sin 2(t-\tau)\,d\tau$"
    ),

    124: (
        r"$(s^2+s-6)Y = 1$ より $Y = \dfrac{1}{(s+3)(s-2)} = \dfrac{1}{5}\!\left(\dfrac{1}{s-2}-\dfrac{1}{s+3}\right)$"
        "\n\n"
        r"$y(t) = \dfrac{1}{5}(e^{2t}-e^{-3t})$"
    ),

    # ============================
    # 3章 フーリエ解析 — Basic
    # ============================
    140: (
        r"$m \neq n$ のとき：積和公式より $\displaystyle\int_{-1}^{1}\cos m\pi x\cos n\pi x\,dx = 0$"
        "\n\n"
        r"$m = n$ のとき：$\displaystyle\int_{-1}^{1}\cos^2 n\pi x\,dx = 1$"
    ),

    141: (
        r"$a_0 = \dfrac{1}{2\pi}\displaystyle\int_{-\pi}^{0} x\,dx = -\dfrac{\pi}{4}$"
        "\n\n"
        r"$a_n = \dfrac{1}{\pi}\displaystyle\int_{-\pi}^{0} x\cos nx\,dx = \dfrac{1-(-1)^n}{n^2\pi}$"
        "\n\n"
        r"$b_n = \dfrac{1}{\pi}\displaystyle\int_{-\pi}^{0} x\sin nx\,dx = \dfrac{(-1)^{n+1}}{n}$"
        "\n\n"
        r"$f(x) = -\dfrac{\pi}{4} + \displaystyle\sum_{n=1}^{\infty}\biggl[\dfrac{1-(-1)^n}{n^2\pi}\cos nx$"
        "\n\n"
        r"$\qquad + \dfrac{(-1)^{n+1}}{n}\sin nx\biggr]$"
    ),

    142: [
        (
            r"$a_0 = \dfrac{1}{2}\displaystyle\int_{-1}^{0}2\,dx + \dfrac{1}{2}\int_0^1 1\,dx = \dfrac{3}{2}$"
            "\n\n"
            r"$a_n = \displaystyle\int_{-1}^{0}2\cos n\pi x\,dx + \int_0^1 \cos n\pi x\,dx = \dfrac{\sin n\pi}{n\pi} = 0$"
            "\n\n"
            r"$b_n = \displaystyle\int_{-1}^{0}2\sin n\pi x\,dx + \int_0^1 \sin n\pi x\,dx = -\dfrac{1+(-1)^n}{n\pi}+\dfrac{2(1-(-1)^n)}{n\pi}$"
            "\n\n"
            r"$= \dfrac{1-3(-1)^n}{n\pi}$"
            "\n\n"
            r"$f(x) = \dfrac{3}{4} + \displaystyle\sum_{n=1}^{\infty}\dfrac{1-3(-1)^n}{2n\pi}\sin n\pi x$"
        ),
        (
            r"周期 $2l=6$，$l=3$ として"
            "\n"
            r"$a_0 = \dfrac{1}{3}\displaystyle\int_{-3}^{0}3\,dx + \dfrac{1}{3}\int_0^3 x\,dx = 3+\dfrac{3}{2} = \dfrac{9}{2}$"
            "\n\n"
            r"$a_n = \dfrac{1}{3}\displaystyle\int_{-3}^{0}3\cos\dfrac{n\pi x}{3}\,dx + \dfrac{1}{3}\int_0^3 x\cos\dfrac{n\pi x}{3}\,dx = \dfrac{3((-1)^n-1)}{n^2\pi^2}$"
            "\n\n"
            r"$b_n = \dfrac{1}{3}\displaystyle\int_{-3}^{0}3\sin\dfrac{n\pi x}{3}\,dx + \dfrac{1}{3}\int_0^3 x\sin\dfrac{n\pi x}{3}\,dx = -\dfrac{3}{n\pi}$"
            "\n\n"
            r"$g(x) = \dfrac{9}{4}-\dfrac{6}{\pi^2}\displaystyle\sum_{k=0}^{\infty}\dfrac{1}{(2k+1)^2}\cos\dfrac{(2k+1)\pi x}{3}-\dfrac{3}{\pi}\sum_{n=1}^{\infty}\dfrac{1}{n}\sin\dfrac{n\pi x}{3}$"
        ),
    ],

    143: [
        (
            r"$f(x) = -x$ は奇関数なので $a_0=0$，$a_n=0$．"
            "\n\n"
            r"$b_n = \dfrac{2}{2}\displaystyle\int_0^2 (-x)\sin\dfrac{n\pi x}{2}\,dx = \dfrac{4(-1)^n}{n\pi}$"
            "\n\n"
            r"$f(x) = \displaystyle\sum_{n=1}^{\infty}\dfrac{4(-1)^n}{n\pi}\sin\dfrac{n\pi x}{2}$"
        ),
        (
            r"$g(x) = 1-x^2$ は偶関数なので $b_n=0$．"
            "\n\n"
            r"$a_0 = \displaystyle\int_0^1(1-x^2)\,dx = \dfrac{2}{3}$"
            "\n\n"
            r"$a_n = 2\displaystyle\int_0^1(1-x^2)\cos n\pi x\,dx = \dfrac{4(-1)^{n+1}}{n^2\pi^2}$"
            "\n\n"
            r"$g(x) = \dfrac{1}{3}+\displaystyle\sum_{n=1}^{\infty}\dfrac{4(-1)^{n+1}}{n^2\pi^2}\cos n\pi x$"
        ),
    ],

    144: (
        r"問題141で $x=0$ を代入すると $f(0^-)+f(0^+)$ の平均に収束する．"
        "\n"
        r"$x=-\pi$ を代入すると（不連続点の平均値を利用して）"
        "\n\n"
        r"$-\dfrac{\pi}{4}-\dfrac{2}{\pi}\!\left(\dfrac{1}{1^2}+\dfrac{1}{3^2}+\dfrac{1}{5^2}+\cdots\right) = -\dfrac{\pi}{2}$"
        "\n\n"
        r"整理して $\dfrac{1}{1^2}+\dfrac{1}{3^2}+\dfrac{1}{5^2}+\cdots = \dfrac{\pi^2}{8}$"
    ),

    145: (
        r"$c_n = \dfrac{1}{2}\displaystyle\int_{-1}^{1}f(x)e^{-in\pi x}\,dx = \dfrac{1}{2}\int_{-1}^{0}2e^{-in\pi x}\,dx$"
        "\n\n"
        r"$n \neq 0$：$c_n = \dfrac{1}{2}\!\left[\dfrac{2e^{-in\pi x}}{-in\pi}\right]_{-1}^{0} = \dfrac{1-(-1)^n}{in\pi}$"
        "\n"
        r"$n=0$：$c_0 = 1$"
        "\n\n"
        r"$f(x) = 1 + \displaystyle\sum_{\substack{n=-\infty\\n\neq 0}}^{\infty}\dfrac{1-(-1)^n}{in\pi}e^{in\pi x}$"
    ),

    146: (
        r"$c_n = \dfrac{1}{4}\displaystyle\int_{-2}^{2}|x|e^{-in\pi x/2}\,dx$"
        "\n\n"
        r"$n=0$：$c_0 = \dfrac{1}{4}\displaystyle\int_{-2}^{2}|x|\,dx = 1$"
        "\n\n"
        r"$n\neq 0$：$|x|$ は偶関数なので $c_n = \dfrac{2((-1)^n-1)}{n^2\pi^2}$"
        "\n\n"
        r"$f(x) = 1 + \displaystyle\sum_{\substack{n=-\infty\\n\neq 0}}^{\infty}\dfrac{2((-1)^n-1)}{n^2\pi^2}e^{in\pi x/2}$"
    ),

    152: (
        r"$\mathcal{F}[f] = \displaystyle\int_{-\infty}^{\infty}f(x)e^{-iux}\,dx = \int_0^\infty e^{-x}e^{-iux}\,dx = \int_0^\infty e^{-(1+iu)x}\,dx$"
        "\n\n"
        r"$= \dfrac{1}{1+iu}$"
    ),

    153: [
        (
            r"$\mathcal{F}[f] = \displaystyle\int_{-3}^{0}2e^{-iux}\,dx = \dfrac{2}{iu}(1-e^{3iu})$"
        ),
        (
            r"$\mathcal{F}[g] = \displaystyle\int_0^1 xe^{-iux}\,dx$"
            "\n\n"
            r"部分積分して $= \dfrac{e^{-iu}}{u^2}(1+iu)-\dfrac{1}{u^2} = \dfrac{(1+iu)e^{-iu}-1}{u^2}$"
        ),
    ],

    154: [
        (
            r"$F(u) = \dfrac{1}{1+iu}$ をフーリエの積分定理に代入して"
            "\n"
            r"$\dfrac{1}{2\pi}\displaystyle\int_{-\infty}^{\infty}\dfrac{e^{iux}}{1+iu}\,du = \dfrac{1}{2\pi}\int_{-\infty}^{\infty}\dfrac{1-iu}{1+u^2}e^{iux}\,du$"
            "\n\n"
            r"不連続点 $x=0$ では $\dfrac{f(0^+)+f(0^-)}{2} = \dfrac{1}{2}$ に収束する．"
        ),
        (
            r"(1)で $x=0$ を代入すると"
            "\n"
            r"$\dfrac{1}{2\pi}\displaystyle\int_{-\infty}^{\infty}\dfrac{1}{1+u^2}\,du = \dfrac{1}{2}$"
            "\n\n"
            r"よって $\displaystyle\int_{-\infty}^{\infty}\dfrac{1}{1+u^2}\,du = \pi$"
        ),
    ],

    155: (
        r"$f(x)$ は奇関数なので，フーリエ正弦変換"
        "\n"
        r"$\mathcal{F}_s[f] = \displaystyle\int_{-\infty}^{\infty}f(x)\sin ux\,dx$"
        "\n\n"
        r"$= 2\displaystyle\int_0^1(-x+1)\sin ux\,dx$"
        "\n\n"
        r"部分積分して $= \dfrac{2(u-\sin u)}{u^2}$"
    ),

    156: (
        r"$\mathcal{F}[f(ax)] = \displaystyle\int_{-\infty}^{\infty}f(ax)e^{-iux}\,dx$"
        "\n\n"
        r"$ax=t$ と置換すると $dx = dt/a$（$a>0$），$dx = dt/a$（$a<0$）"
        "\n\n"
        r"$= \dfrac{1}{|a|}\displaystyle\int_{-\infty}^{\infty}f(t)e^{-i(u/a)t}\,dt = \dfrac{1}{|a|}F\!\left(\dfrac{u}{a}\right)$"
    ),

    157: (
        r"$\mathcal{F}[f*g] = \mathcal{F}[f]\cdot\mathcal{F}[g]$"
        "\n\n"
        r"$\mathcal{F}[f] = \dfrac{2}{iu}(1-e^{3iu})$，$\mathcal{F}[g] = \dfrac{(1+iu)e^{-iu}-1}{u^2}$"
        "\n\n"
        r"$\mathcal{F}[f*g] = \dfrac{2}{iu}\cdot(1-e^{3iu})\cdot\dfrac{(1+iu)e^{-iu}-1}{u^2}$"
    ),

    158: [
        r"$a=1/4$ として $\mathcal{F}[e^{-x^2/4}] = \sqrt{4\pi}\,e^{-u^2} = 2\sqrt{\pi}\,e^{-u^2}$",
        (
            r"微分法則 $\mathcal{F}[xf(x)] = i\dfrac{d}{du}F(u)$ より"
            "\n"
            r"$\mathcal{F}[xe^{-x^2/4}] = i\cdot(-2u)\cdot 2\sqrt{\pi}\,e^{-u^2} = -4i\sqrt{\pi}\,ue^{-u^2}$"
        ),
        (
            r"$\mathcal{F}[x^2 e^{-x^2/4}] = (i)^2\dfrac{d^2}{du^2}(2\sqrt{\pi}\,e^{-u^2})$"
            "\n\n"
            r"$= -2\sqrt{\pi}(4u^2-2)e^{-u^2} = 2\sqrt{\pi}(2-4u^2)e^{-u^2}$"
        ),
    ],

    159: (
        r"$\mathcal{F}[e^{-ax^2}] = \sqrt{\dfrac{\pi}{a}}\,e^{-u^2/(4a)}$ で $a=3$，$u$ と $x$ の役割を入れ替えて"
        "\n\n"
        r"$\mathcal{F}^{-1}[e^{-3u^2}] = \dfrac{1}{2\sqrt{3\pi}}\,e^{-x^2/12}$"
    ),

    160: [
        (
            r"$\mathcal{F}[e^{-x^2/4}] = 2\sqrt{\pi}\,e^{-u^2}$，$\mathcal{F}[xe^{-x^2/4}] = -4i\sqrt{\pi}\,ue^{-u^2}$"
            "\n\n"
            r"$\mathcal{F}[e^{-x^2/4}*xe^{-x^2/4}] = 2\sqrt{\pi}\,e^{-u^2}\cdot(-4i\sqrt{\pi}\,ue^{-u^2}) = -8\pi iu\,e^{-2u^2}$"
        ),
        (
            r"$\mathcal{F}^{-1}[-8\pi iu\,e^{-2u^2}]$ を計算する．"
            "\n\n"
            r"$e^{-2u^2}$ の逆変換と微分法則を用いて"
            "\n"
            r"$e^{-x^2/4}*xe^{-x^2/4} = \sqrt{\dfrac{\pi}{2}}\,xe^{-x^2/8}$"
        ),
    ],

    161: (
        r"$f(x) = |x|$（$|x|\leq 1$），周期 2 のフーリエ係数"
        "\n\n"
        r"$c_n = \dfrac{1}{2}\displaystyle\int_{-1}^{1}|x|e^{-in\pi x}\,dx$"
        "\n\n"
        r"$c_0 = \dfrac{1}{2}$，$c_n = \dfrac{(-1)^n - 1}{n^2\pi^2}$（$n \neq 0$）"
        "\n\n"
        r"スペクトル $|c_n|$：$|c_0|=\dfrac{1}{2}$，$|c_n|=\dfrac{|(-1)^n-1|}{n^2\pi^2}$"
    ),

    162: (
        r"非周期関数なのでフーリエ変換を用いる．"
        "\n\n"
        r"$F(u) = \displaystyle\int_{-1}^{1}|x|e^{-iux}\,dx = 2\int_0^1 x\cos ux\,dx = \dfrac{2(\cos u + u\sin u - 1)}{u^2}$"
        "\n\n"
        r"スペクトル $|F(u)| = \dfrac{2|\cos u + u\sin u - 1|}{u^2}$"
    ),

    # ============================
    # 3章 フーリエ解析 — Check
    # ============================
    147: [
        (
            r"$a_0 = \dfrac{1}{2\pi}\displaystyle\int_{-\pi}^{\pi}f(x)\,dx = -\dfrac{1}{2}$"
            "\n\n"
            r"$a_n = 0$（$f(x)+\dfrac{1}{2}$ が奇関数），$b_n = \dfrac{3((-1)^n-1)}{n\pi}$"
            "\n\n"
            r"$f(x) = -\dfrac{1}{2}-\dfrac{6}{\pi}\displaystyle\sum_{k=0}^{\infty}\dfrac{1}{2k+1}\sin(2k+1)x$"
        ),
        (
            r"周期 $2l=4$，$l=2$ として"
            "\n"
            r"$a_0 = \dfrac{1}{2}\displaystyle\int_{-2}^{0}(x+2)\,dx = 1$"
            "\n\n"
            r"$a_n = \dfrac{1}{2}\displaystyle\int_{-2}^{0}(x+2)\cos\dfrac{n\pi x}{2}\,dx = \dfrac{2(1-(-1)^n)}{n^2\pi^2}$"
            "\n\n"
            r"$b_n = \dfrac{1}{2}\displaystyle\int_{-2}^{0}(x+2)\sin\dfrac{n\pi x}{2}\,dx = -\dfrac{2}{n\pi}$"
            "\n\n"
            r"$g(x) = \dfrac{1}{2}+\dfrac{4}{\pi^2}\displaystyle\sum_{k=0}^{\infty}\dfrac{1}{(2k+1)^2}\cos\dfrac{(2k+1)\pi x}{2}-\dfrac{2}{\pi}\sum_{n=1}^{\infty}\dfrac{1}{n}\sin\dfrac{n\pi x}{2}$"
        ),
        (
            r"$h(x) = |\sin x|$ は偶関数（周期 $\pi$）なので $b_n=0$．"
            "\n\n"
            r"$a_0 = \dfrac{2}{\pi}\displaystyle\int_0^{\pi/2}\sin x\,dx = \dfrac{2}{\pi}$"
            "\n\n"
            r"$a_n = \dfrac{2}{\pi}\cdot\dfrac{2(1+(-1)^n)}{1-4n^2}$"
            "\n\n"
            r"$h(x) = \dfrac{2}{\pi}-\dfrac{4}{\pi}\displaystyle\sum_{n=1}^{\infty}\dfrac{\cos 2nx}{4n^2-1}$"
        ),
    ],

    148: (
        r"問題147(1)で $x=\pi/2$ を代入すると $f(\pi/2)=1$ に収束する．"
        "\n\n"
        r"$1 = -\dfrac{1}{2}-\dfrac{6}{\pi}\!\left(-\dfrac{1}{1}+\dfrac{1}{3}-\dfrac{1}{5}+\cdots\right)$"
        "\n\n"
        r"整理して $1-\dfrac{1}{3}+\dfrac{1}{5}-\dfrac{1}{7}+\cdots = \dfrac{\pi}{4}$"
    ),

    149: [
        (
            r"$c_n = \dfrac{1}{2}\displaystyle\int_{-1}^{1}(2x+1)e^{-in\pi x}\,dx$"
            "\n\n"
            r"$c_0 = \dfrac{1}{2}\displaystyle\int_{-1}^{1}(2x+1)\,dx = 1$"
            "\n\n"
            r"$n\neq 0$：部分積分より $c_n = \dfrac{2(-1)^{n+1}}{in\pi}$"
            "\n\n"
            r"$f(x) = 1 + \displaystyle\sum_{\substack{n=-\infty \\ n\neq 0}}^{\infty}\dfrac{2(-1)^{n+1}}{in\pi}\,e^{in\pi x}$"
        ),
        (
            r"$c_n = \dfrac{1}{6}\displaystyle\int_{-3}^{3}g(x)e^{-in\pi x/3}\,dx$"
            "\n\n"
            r"$c_0 = 0$，$c_n = \dfrac{(-1)^n-1}{in\pi}$（$n\neq 0$）"
        ),
    ],

    163: [
        (
            r"$\mathcal{F}[f] = \displaystyle\int_1^2 e^{-iux}\,dx = \dfrac{e^{-iu}-e^{-2iu}}{iu}$"
        ),
        (
            r"$\mathcal{F}[g] = \displaystyle\int_0^2 (2-x)e^{-iux}\,dx$"
            "\n\n"
            r"部分積分して $= \dfrac{2}{iu}-\dfrac{e^{-2iu}-1}{u^2}+\dfrac{2e^{-2iu}}{iu}$"
            "\n\n"
            r"整理して $= \dfrac{1-e^{-2iu}(1+2iu)}{u^2}$"
        ),
        (
            r"$\mathcal{F}[h] = \displaystyle\int_{-\infty}^{0} e^{3x}e^{-iux}\,dx = \dfrac{1}{3-iu}$"
        ),
    ],

    164: (
        r"問題163(1)の $f(x)$ にフーリエの積分定理を適用し，$x=1$（不連続点）で"
        "\n"
        r"$\dfrac{f(1^+)+f(1^-)}{2} = \dfrac{1}{2}$ に収束することを利用する．"
        "\n\n"
        r"$\dfrac{1}{2\pi}\displaystyle\int_{-\infty}^{\infty}\dfrac{e^{-iu}-e^{-2iu}}{iu}e^{iu}\,du = \dfrac{1}{2}$"
        "\n\n"
        r"$\dfrac{1}{2\pi}\displaystyle\int_{-\infty}^{\infty}\dfrac{1-e^{-iu}}{iu}\,du = \dfrac{1}{2}$"
        "\n\n"
        r"虚部を取り出して $\displaystyle\int_{-\infty}^{\infty}\dfrac{\sin u}{u}\,du = \pi$"
    ),

    165: (
        r"$f(x)$ は奇関数なので"
        "\n"
        r"$\mathcal{F}_s[f] = 2\displaystyle\int_0^2 \!\left(-\dfrac{x}{3}\right)\sin ux\,dx = -\dfrac{2}{3}\int_0^2 x\sin ux\,dx$"
        "\n\n"
        r"部分積分して $= -\dfrac{2}{3}\!\left[\dfrac{\sin 2u - 2u\cos 2u}{u^2}\right]$"
    ),

    166: (
        r"$\mathcal{F}[e^{-|x|}] = \dfrac{2}{1+u^2}$ と相似性 $\mathcal{F}[f(ax)] = \dfrac{1}{|a|}F(u/a)$ より"
        "\n\n"
        r"$\mathcal{F}[e^{-a|x|}] = \dfrac{1}{a}\cdot\dfrac{2}{1+(u/a)^2} = \dfrac{2a}{a^2+u^2}$"
    ),

    167: (
        r"$\mathcal{F}[e^{-|x|}*e^{-2|x|}] = \mathcal{F}[e^{-|x|}]\cdot\mathcal{F}[e^{-2|x|}]$"
        "\n\n"
        r"$= \dfrac{2}{1+u^2}\cdot\dfrac{4}{4+u^2} = \dfrac{8}{(1+u^2)(4+u^2)}$"
    ),

    168: [
        (
            r"$\mathcal{F}[e^{-x^2/a}] = \sqrt{a\pi}\,e^{-au^2/4}$，$\mathcal{F}[xe^{-x^2/b}] = -ib\sqrt{b\pi}\,\dfrac{u}{2}\,e^{-bu^2/4}$"
            "\n\n"
            r"たたみ込み定理より"
            "\n"
            r"$\mathcal{F}[e^{-x^2/a}*xe^{-x^2/b}] = \sqrt{a\pi}\,e^{-au^2/4}\cdot\!\left(-\dfrac{ib\sqrt{b\pi}\,u}{2}\,e^{-bu^2/4}\right)$"
            "\n\n"
            r"$= -\dfrac{\pi b\sqrt{ab}}{2}\,iu\,e^{-(a+b)u^2/4}$"
        ),
        (
            r"(1)の逆フーリエ変換を計算する．"
            "\n"
            r"$iu\,e^{-cu^2}$ の逆変換（$c=(a+b)/4$）は $\dfrac{x}{2c}\cdot\dfrac{1}{2\sqrt{\pi c}}\,e^{-x^2/(4c)}$ に比例する．"
            "\n\n"
            r"整理して $e^{-x^2/a}*xe^{-x^2/b} = \dfrac{b\sqrt{ab\pi}}{(a+b)\sqrt{a+b}}\,xe^{-x^2/(a+b)}$"
        ),
    ],

    169: [
        (
            r"$f(x) = 1-|x|$（$|x|\leq 2$），周期 4 のフーリエ係数"
            "\n\n"
            r"$c_0 = \dfrac{1}{4}\displaystyle\int_{-2}^{2}(1-|x|)\,dx = 0$"
            "\n\n"
            r"偶関数なので $c_n = \dfrac{1}{2}\displaystyle\int_0^2(1-x)\cos\dfrac{n\pi x}{2}\,dx = \dfrac{2(1-(-1)^n)}{n^2\pi^2}$"
            "\n\n"
            r"スペクトル：$|c_n| = \dfrac{4}{n^2\pi^2}$（$n$ が奇数），$|c_n|=0$（$n$ が偶数）"
        ),
        (
            r"非周期関数のフーリエ変換"
            "\n"
            r"$F(u) = \displaystyle\int_{-2}^{2}(1-|x|)e^{-iux}\,dx$"
            "\n\n"
            r"偶関数なので $F(u) = 2\displaystyle\int_0^2(1-x)\cos ux\,dx = \dfrac{2(1-\cos 2u - u\sin 2u)}{u^2}$"
            "\n\n"
            r"スペクトル $|F(u)| = \dfrac{2|1-\cos 2u - u\sin 2u|}{u^2}$"
        ),
    ],
}


def main():
    yaml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "applied_math_problems.yaml",
    )

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    updated = 0

    for chap_key in ["chapter2", "chapter3"]:
        if chap_key not in data:
            continue
        for section in ["basic", "check"]:
            if section not in data[chap_key] or not data[chap_key][section]:
                continue
            for item in data[chap_key][section]:
                no = item.get("no", item.get(False, 0))
                if no in ANSWERS:
                    item["answer"] = ANSWERS[no]
                    updated += 1

    # 書き出し（yaml.dump は日本語が壊れるので、元ファイルを正規表現で書き換える）
    # → 簡易方式：yaml.dump で書き出し
    # PyYAML の dump は 'no' を boolean に変換してしまうため、
    # 元の YAML を行単位で処理する方式に切り替える

    # 方針：元ファイルを読み直し、answer: "" の行を置き換える
    with open(yaml_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 問題番号の状態追跡
    current_no = None
    current_answer_index = 0  # リスト型解答のインデックス
    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 問題番号の検出
        if stripped.startswith("- no:"):
            try:
                current_no = int(stripped.split(":")[1].strip())
            except ValueError:
                current_no = None
            current_answer_index = 0
            output_lines.append(line)
            i += 1
            continue

        # answer フィールドの検出と置換
        if current_no in ANSWERS:
            ans = ANSWERS[current_no]

            # 単一 answer: "" の場合（常に | ブロック形式を使用）
            if stripped == 'answer: ""' and isinstance(ans, str):
                indent = line[:len(line) - len(line.lstrip())]
                output_lines.append(f'{indent}answer: |\n')
                for aline in ans.split("\n"):
                    output_lines.append(f'{indent}  {aline}\n')
                i += 1
                continue

            # リスト型 answer の場合: - "" を検出（常に | ブロック形式）
            if stripped == '- ""' and isinstance(ans, list):
                indent = line[:len(line) - len(line.lstrip())]
                if current_answer_index < len(ans):
                    a = ans[current_answer_index]
                    output_lines.append(f'{indent}- |\n')
                    for aline in a.split("\n"):
                        output_lines.append(f'{indent}  {aline}\n')
                    current_answer_index += 1
                else:
                    output_lines.append(line)
                i += 1
                continue

        output_lines.append(line)
        i += 1

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"Updated {updated} problems with answers.")
    print("Done.")


if __name__ == "__main__":
    main()
