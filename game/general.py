from wecs.core import Component


@Component()
class Speed:
    current: float = 0.0
    min: float = 0.0
    max: float = None

    def accelerate(self, by, max=None, min=None):
        self.current += by * globalClock.dt

        if max is not None and self.current > max:
            self.current = max

        if min is not None and self.current < min:
            self.current = min

        if self.max is not None and self.current > self.max:
            self.current = self.max
        elif self.current < self.min:
            self.current = self.min
