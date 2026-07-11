from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen


class PoseRenderer:

    CONNECTIONS = [

        (11,13),(13,15),
        (12,14),(14,16),

        (11,12),

        (11,23),
        (12,24),

        (23,24),

        (23,25),
        (25,27),

        (24,26),
        (26,28),

        (27,31),
        (28,32)

    ]

    def draw(
        self,
        painter: QPainter,
        landmarks,
        width,
        height,
    ):

        if landmarks is None:
            return

        pen = QPen(
            QColor(0,255,0),
            3,
        )

        painter.setPen(pen)

        painter.setBrush(
            QColor(255,60,60)
        )

        for start,end in self.CONNECTIONS:

            a = landmarks[start]
            b = landmarks[end]

            painter.drawLine(
                QPointF(a.x*width,a.y*height),
                QPointF(b.x*width,b.y*height)
            )

        for lm in landmarks:

            painter.drawEllipse(
                QPointF(
                    lm.x*width,
                    lm.y*height
                ),
                4,
                4
            )