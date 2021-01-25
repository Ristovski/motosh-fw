#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/timer.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/systick.h>

static volatile uint32_t systicks = 0;

void sys_tick_handler(void)
{
	systicks++;
}

static void delay(uint32_t ticks)
{
	uint32_t future_ticks = systicks + ticks;
	while (future_ticks > systicks);
}

static void gpio_setup()
{
	gpio_mode_setup(GPIOB, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO1);
	gpio_toggle(GPIOB, GPIO1);
}

static void clock_setup()
{
	rcc_periph_clock_enable(RCC_GPIOB);

	/* 72MHz / 8 => 9000000 counts per second */
	systick_set_clocksource(STK_CSR_CLKSOURCE_AHB_DIV8);

	/* 9000000/9000 = 1000 overflows per second - every 1ms one interrupt */
	/* SysTick interrupt every N clock pulses: set reload to N-1 */
	systick_set_reload(8999);

	systick_interrupt_enable();
	systick_counter_enable();
}
int main()
{
	clock_setup();
	gpio_setup();

	for (int i = 0; i < 5; ++i)
	{
		gpio_toggle(GPIOB, GPIO1);
		delay(500);
	}

	while(1);
}
