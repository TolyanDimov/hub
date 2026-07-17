#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Создаёт автономную интерактивную 3D HTML-модель.

Сцены:
1. Полуокружность: πr = 3r + (π - 3)r
2. Цикл: 0 → 1 → 2 → 3 → 4 ≡ 0
3. Симметрия нулей и линия Re(s) = 1/2
4. Простые числа на логарифмической винтовой линии
5. Сравнение γ_n с (n + 1)/(π - 3)

Запуск:
    python scripts/riemann_3d_experiment.py

Результат:
    demo/riemann_3d_experiment.html
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "demo" / "riemann_3d_experiment.html"

DELTA = math.pi - 3.0

# Единая палитра сайта: уголь, лунный камень, бронза и красный акцент.
INK = "#090907"
PANEL = "#15130f"
STONE = "#2a251d"
IVORY = "#e7deca"
MUTED = "#9b917f"
BRONZE = "#b89a68"
GOLD = "#d8b77d"
RED = "#a52d23"
COLORWAY = [GOLD, RED, "#c8bda8", "#806b4c", "#efe4ce", "#60423a"]
AXIS_STYLE = {
    "showbackground": True,
    "backgroundcolor": PANEL,
    "gridcolor": "#3b3327",
    "zerolinecolor": BRONZE,
    "color": MUTED,
}

GAMMAS = np.array(
    [
        14.134725141734694,
        21.022039638771555,
        25.01085758014569,
        30.424876125859513,
        32.93506158773919,
        37.58617815882567,
        40.9187190121475,
        43.327073280915,
        48.00515088116716,
        49.7738324776723,
        52.97032147771446,
        56.44624769706339,
    ],
    dtype=float,
)


def primes_up_to(limit: int) -> list[int]:
    """Возвращает простые числа до limit включительно."""
    if limit < 2:
        return []

    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False

    for value in range(2, int(limit**0.5) + 1):
        if sieve[value]:
            sieve[value * value : limit + 1 : value] = False

    return np.flatnonzero(sieve).tolist()


def add_trace(
    fig: go.Figure,
    groups: dict[str, list[int]],
    group: str,
    trace,
) -> None:
    fig.add_trace(trace)
    groups.setdefault(group, []).append(len(fig.data) - 1)


def line3d(
    x: Iterable[float],
    y: Iterable[float],
    z: Iterable[float],
    *,
    name: str,
    width: float = 5,
    hovertext: list[str] | None = None,
    showlegend: bool = True,
    opacity: float = 1.0,
) -> go.Scatter3d:
    return go.Scatter3d(
        x=list(x),
        y=list(y),
        z=list(z),
        mode="lines",
        name=name,
        line={"width": width},
        hovertext=hovertext,
        hoverinfo="text" if hovertext else "name",
        showlegend=showlegend,
        opacity=opacity,
    )


def marker3d(
    x: Iterable[float],
    y: Iterable[float],
    z: Iterable[float],
    *,
    name: str,
    text: list[str],
    size: float | list[float] = 7,
    symbol: str = "circle",
    showlegend: bool = True,
) -> go.Scatter3d:
    return go.Scatter3d(
        x=list(x),
        y=list(y),
        z=list(z),
        mode="markers+text",
        name=name,
        text=text,
        textposition="top center",
        marker={"size": size, "symbol": symbol, "opacity": 0.9},
        hovertext=text,
        hoverinfo="text",
        showlegend=showlegend,
    )


def build_figure(radius: float = 3.0, prime_limit: int = 199) -> go.Figure:
    fig = go.Figure()
    groups: dict[str, list[int]] = {}

    # ------------------------------------------------------------
    # 1. Полуокружность и остаток π - 3
    # ------------------------------------------------------------
    group = "pi_radius"

    theta_full = np.linspace(0.0, math.pi, 350)
    add_trace(
        fig,
        groups,
        group,
        line3d(
            radius * np.cos(theta_full),
            radius * np.sin(theta_full),
            np.zeros_like(theta_full),
            name="Полуокружность πr",
            width=7,
        ),
    )

    theta_rem = np.linspace(3.0, math.pi, 100)
    add_trace(
        fig,
        groups,
        group,
        line3d(
            radius * np.cos(theta_rem),
            radius * np.sin(theta_rem),
            np.full_like(theta_rem, 0.10),
            name="Остаток (π−3)r",
            width=13,
        ),
    )

    # Диаметр.
    add_trace(
        fig,
        groups,
        group,
        line3d(
            [-radius, radius],
            [0.0, 0.0],
            [0.0, 0.0],
            name="Диаметр",
            width=3,
            opacity=0.55,
        ),
    )

    # Лучи после 0, 1, 2 и 3 радиан.
    for k in (0, 1, 2, 3):
        endpoint_x = radius * math.cos(k)
        endpoint_y = radius * math.sin(k)

        add_trace(
            fig,
            groups,
            group,
            line3d(
                [0.0, endpoint_x],
                [0.0, endpoint_y],
                [0.0, 0.0],
                name="Радиус r" if k == 0 else f"Луч после {k} рад.",
                width=3,
                showlegend=(k == 0),
                opacity=0.72,
            ),
        )

    marks = np.array([0.0, 1.0, 2.0, 3.0, math.pi])
    mark_text = [
        "Начало дуги",
        "После 1 радиана: длина дуги r",
        "После 2 радиан: длина дуги 2r",
        "После 3 радиан: длина дуги 3r",
        f"Конец полуокружности; остаток={(DELTA * radius):.6f}",
    ]

    add_trace(
        fig,
        groups,
        group,
        marker3d(
            radius * np.cos(marks),
            radius * np.sin(marks),
            np.full(len(marks), 0.16),
            name="Точки на дуге",
            text=mark_text,
            size=7,
        ),
    )

    # ------------------------------------------------------------
    # 2. Четырёхфазный цикл
    # ------------------------------------------------------------
    group = "four_cycle"

    cycle_angles = np.linspace(0.0, 2.0 * math.pi, 250)
    add_trace(
        fig,
        groups,
        group,
        line3d(
            np.cos(cycle_angles),
            np.sin(cycle_angles),
            np.zeros_like(cycle_angles),
            name="Окружность фаз",
            width=7,
        ),
    )

    step_angles = np.array(
        [0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]
    )

    add_trace(
        fig,
        groups,
        group,
        line3d(
            np.cos(step_angles),
            np.sin(step_angles),
            np.linspace(0.0, 0.4, len(step_angles)),
            name="Путь 0→4",
            width=6,
        ),
    )

    add_trace(
        fig,
        groups,
        group,
        marker3d(
            np.cos(step_angles),
            np.sin(step_angles),
            np.linspace(0.0, 0.4, len(step_angles)),
            name="Четыре шага",
            text=["0", "1", "2", "3", "4 = 0"],
            size=10,
        ),
    )

    add_trace(
        fig,
        groups,
        group,
        line3d(
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 4.0],
            name="Счёт шагов",
            width=4,
            opacity=0.6,
        ),
    )

    # ------------------------------------------------------------
    # 3. Нули и линия Re(s) = 1/2
    # ------------------------------------------------------------
    group = "zeros"

    y_plane = np.linspace(-60.0, 60.0, 2)
    z_plane = np.linspace(-3.0, 3.0, 2)
    yy, zz = np.meshgrid(y_plane, z_plane)
    xx = np.full_like(yy, 0.5)

    add_trace(
        fig,
        groups,
        group,
        go.Surface(
            x=xx,
            y=yy,
            z=zz,
            name="Плоскость Re(s)=1/2",
            opacity=0.22,
            showscale=False,
            hovertemplate="Re(s)=1/2<extra></extra>",
        ),
    )

    gamma_both = np.concatenate([GAMMAS, -GAMMAS])
    zero_text = [
        f"ρ = 1/2 {'+' if value >= 0 else '−'} {abs(value):.6f}i"
        for value in gamma_both
    ]

    add_trace(
        fig,
        groups,
        group,
        marker3d(
            np.full_like(gamma_both, 0.5),
            gamma_both,
            np.zeros_like(gamma_both),
            name="Пары на линии 1/2",
            text=zero_text,
            size=7,
        ),
    )

    beta = 0.34
    gamma = float(GAMMAS[0])

    quartet_x = [beta, beta, 1.0 - beta, 1.0 - beta]
    quartet_y = [gamma, -gamma, gamma, -gamma]
    quartet_z = [1.0, 1.0, 1.0, 1.0]
    quartet_text = [
        "ρ = β+iγ",
        "conj(ρ) = β−iγ",
        "1−conj(ρ) = (1−β)+iγ",
        "1−ρ = (1−β)−iγ",
    ]

    add_trace(
        fig,
        groups,
        group,
        marker3d(
            quartet_x,
            quartet_y,
            quartet_z,
            name="Четвёрка вне линии",
            text=quartet_text,
            size=10,
            symbol="diamond",
        ),
    )

    rectangle_order = [0, 2, 3, 1, 0]
    add_trace(
        fig,
        groups,
        group,
        line3d(
            [quartet_x[index] for index in rectangle_order],
            [quartet_y[index] for index in rectangle_order],
            [quartet_z[index] for index in rectangle_order],
            name="Связи четвёрки",
            width=4,
            opacity=0.7,
        ),
    )

    add_trace(
        fig,
        groups,
        group,
        line3d(
            [0.5, 0.5],
            [-60.0, 60.0],
            [0.0, 0.0],
            name="Критическая линия",
            width=10,
        ),
    )

    # ------------------------------------------------------------
    # 4. Простые числа на логарифмической винтовой линии
    # ------------------------------------------------------------
    group = "prime_helix"

    primes = np.asarray(primes_up_to(prime_limit), dtype=float)
    u = np.log(primes)

    u_smooth = np.linspace(float(u.min()), float(u.max()), 700)
    add_trace(
        fig,
        groups,
        group,
        line3d(
            np.cos(u_smooth),
            np.sin(u_smooth),
            u_smooth,
            name="Винтовая линия u=log p",
            width=5,
            opacity=0.65,
        ),
    )

    weights = np.log(primes) / np.sqrt(primes)
    marker_sizes = 5.0 + 18.0 * weights / weights.max()

    prime_hover = [
        (
            f"p={int(p)}<br>"
            f"log p={up:.6f}<br>"
            f"вес log(p)/sqrt(p)={weight:.6f}<br>"
            f"фаза при t=1: −{up:.6f}"
        )
        for p, up, weight in zip(primes, u, weights)
    ]

    add_trace(
        fig,
        groups,
        group,
        go.Scatter3d(
            x=np.cos(u),
            y=np.sin(u),
            z=u,
            mode="markers",
            name="Простые числа",
            marker={
                "size": marker_sizes,
                "opacity": 0.9,
                "color": u,
                "colorscale": [[0.0, INK], [0.28, STONE], [0.58, BRONZE], [0.82, GOLD], [1.0, IVORY]],
                "showscale": True,
                "colorbar": {"title": "log p", "len": 0.55},
            },
            hovertext=prime_hover,
            hoverinfo="text",
        ),
    )

    for prime, up in zip(primes[:12], u[:12]):
        add_trace(
            fig,
            groups,
            group,
            line3d(
                [0.0, math.cos(float(up))],
                [0.0, math.sin(float(up))],
                [float(up), float(up)],
                name=f"p={int(prime)}",
                width=2,
                showlegend=False,
                opacity=0.55,
            ),
        )

    # ------------------------------------------------------------
    # 5. Сравнение с постоянным шагом на основе π - 3
    # ------------------------------------------------------------
    group = "delta_compare"

    n = np.arange(1, len(GAMMAS) + 1, dtype=float)
    model = (n + 1.0) / DELTA

    add_trace(
        fig,
        groups,
        group,
        go.Scatter3d(
            x=n,
            y=GAMMAS,
            z=np.zeros_like(n),
            mode="lines+markers",
            name="Настоящие γₙ",
            marker={"size": 7},
            line={"width": 7},
            hovertext=[
                f"n={int(index)}<br>γₙ={value:.9f}"
                for index, value in zip(n, GAMMAS)
            ],
            hoverinfo="text",
        ),
    )

    add_trace(
        fig,
        groups,
        group,
        go.Scatter3d(
            x=n,
            y=model,
            z=np.ones_like(n),
            mode="lines+markers",
            name="(n+1)/(π−3)",
            marker={"size": 7},
            line={"width": 7},
            hovertext=[
                f"n={int(index)}<br>модель={value:.9f}"
                for index, value in zip(n, model)
            ],
            hoverinfo="text",
        ),
    )

    for index, real_value, model_value in zip(n, GAMMAS, model):
        hover = (
            f"n={int(index)}<br>"
            f"γₙ={real_value:.9f}<br>"
            f"модель={model_value:.9f}<br>"
            f"разница={model_value - real_value:+.9f}"
        )

        add_trace(
            fig,
            groups,
            group,
            line3d(
                [float(index), float(index)],
                [float(real_value), float(model_value)],
                [0.0, 1.0],
                name=f"Ошибка n={int(index)}",
                width=3,
                hovertext=[hover, hover],
                showlegend=False,
                opacity=0.72,
            ),
        )

    # ------------------------------------------------------------
    # Переключение сцен
    # ------------------------------------------------------------
    trace_count = len(fig.data)

    def visibility_mask(group_name: str) -> list[bool]:
        mask = [False] * trace_count
        for trace_index in groups[group_name]:
            mask[trace_index] = True
        return mask

    scene_settings = {
        "π и радиус": {
            "group": "pi_radius",
            "title": "Полуокружность: πr = 3r + (π−3)r",
            "x_title": "X",
            "y_title": "Y",
            "z_title": "визуальный слой",
            "x_range": [-radius * 1.25, radius * 1.25],
            "y_range": [-0.5, radius * 1.35],
            "z_range": [-0.4, 0.8],
            "camera": {"eye": {"x": 1.35, "y": -1.65, "z": 1.0}},
        },
        "Цикл 0→4": {
            "group": "four_cycle",
            "title": "Четыре шага и возвращение к нулевой фазе",
            "x_title": "X",
            "y_title": "Y",
            "z_title": "номер повторения",
            "x_range": [-1.4, 1.4],
            "y_range": [-1.4, 1.4],
            "z_range": [-0.5, 4.5],
            "camera": {"eye": {"x": 1.45, "y": 1.45, "z": 1.2}},
        },
        "Нули и 1/2": {
            "group": "zeros",
            "title": "Симметрия нулей относительно Re(s)=1/2",
            "x_title": "Re(s)",
            "y_title": "Im(s)",
            "z_title": "визуальный слой",
            "x_range": [0.0, 1.0],
            "y_range": [-60.0, 60.0],
            "z_range": [-3.0, 3.0],
            "camera": {"eye": {"x": 2.15, "y": -1.15, "z": 0.7}},
        },
        "Простые и log p": {
            "group": "prime_helix",
            "title": "Простые числа на логарифмической винтовой линии",
            "x_title": "cos(log p)",
            "y_title": "sin(log p)",
            "z_title": "log p",
            "x_range": [-1.3, 1.3],
            "y_range": [-1.3, 1.3],
            "z_range": [0.0, float(u.max()) + 0.5],
            "camera": {"eye": {"x": 1.55, "y": 1.55, "z": 1.15}},
        },
        "π−3 и нули": {
            "group": "delta_compare",
            "title": "Проверка постоянного шага на основе π−3",
            "x_title": "номер n",
            "y_title": "высота",
            "z_title": "0: нули, 1: модель",
            "x_range": [0.5, len(GAMMAS) + 0.5],
            "y_range": [10.0, float(model.max()) + 5.0],
            "z_range": [-0.4, 1.4],
            "camera": {"eye": {"x": 1.7, "y": -1.6, "z": 1.1}},
        },
    }

    buttons = []

    for label, settings in scene_settings.items():
        buttons.append(
            {
                "label": label,
                "method": "update",
                "args": [
                    {"visible": visibility_mask(settings["group"])},
                    {
                        "title": {
                            "text": settings["title"],
                            "x": 0.5,
                            "xanchor": "center",
                        },
                        "scene": {
                            "xaxis": {
                                "title": settings["x_title"],
                                "range": settings["x_range"],
                                **AXIS_STYLE,
                            },
                            "yaxis": {
                                "title": settings["y_title"],
                                "range": settings["y_range"],
                                **AXIS_STYLE,
                            },
                            "zaxis": {
                                "title": settings["z_title"],
                                "range": settings["z_range"],
                                **AXIS_STYLE,
                            },
                            "camera": settings["camera"],
                            "aspectmode": "manual",
                            "aspectratio": {"x": 1.2, "y": 1.2, "z": 1.0},
                        },
                    },
                ],
            }
        )

    default = scene_settings["Нули и 1/2"]
    default_mask = visibility_mask(default["group"])

    for trace, is_visible in zip(fig.data, default_mask):
        trace.visible = is_visible

    fig.update_layout(
        template="plotly_dark",
        colorway=COLORWAY,
        paper_bgcolor=INK,
        plot_bgcolor=INK,
        font={"family": "Georgia, Times New Roman, serif", "color": IVORY},
        title={
            "text": default["title"],
            "x": 0.5,
            "xanchor": "center",
        },
        height=860,
        margin={"l": 0, "r": 0, "t": 120, "b": 0},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 0.01,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(9,9,7,0.82)",
            "bordercolor": BRONZE,
            "font": {"color": IVORY},
        },
        updatemenus=[
            {
                "type": "dropdown",
                "direction": "down",
                "x": 0.02,
                "y": 1.12,
                "xanchor": "left",
                "yanchor": "top",
                "buttons": buttons,
                "showactive": True,
                "active": 2,
                "bgcolor": PANEL,
                "bordercolor": BRONZE,
                "font": {"color": IVORY},
            }
        ],
        annotations=[
            {
                "text": (
                    "Выберите сцену в меню. "
                    "Модель можно вращать мышью, приближать колёсиком "
                    "и исследовать наведением на точки."
                ),
                "x": 0.5,
                "y": 1.07,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 14, "color": MUTED},
            }
        ],
        scene={
            "bgcolor": INK,
            "xaxis": {
                "title": default["x_title"],
                "range": default["x_range"],
                **AXIS_STYLE,
            },
            "yaxis": {
                "title": default["y_title"],
                "range": default["y_range"],
                **AXIS_STYLE,
            },
            "zaxis": {
                "title": default["z_title"],
                "range": default["z_range"],
                **AXIS_STYLE,
            },
            "camera": default["camera"],
            "aspectmode": "manual",
            "aspectratio": {"x": 1.2, "y": 1.2, "z": 1.0},
        },
    )

    return fig


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    figure = build_figure()

    pio.write_html(
        figure,
        file=str(OUTPUT),
        include_plotlyjs=True,
        full_html=True,
        auto_open=False,
        config={
            "responsive": True,
            "displaylogo": False,
            "scrollZoom": True,
        },
    )

    print(f"HTML создан: {OUTPUT}")


if __name__ == "__main__":
    main()
