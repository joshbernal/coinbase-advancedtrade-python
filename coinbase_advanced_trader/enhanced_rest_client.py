"""Enhanced REST client for Coinbase Advanced Trading API."""

from typing import Optional, List, Dict, Any
from coinbase.rest import RESTClient
from .services.order_service import OrderService
from .services.fear_and_greed_strategy import FearAndGreedStrategy
from .services.price_service import PriceService
from coinbase_advanced_trader.trading_config import BUY_PRICE_MULTIPLIER, SELL_PRICE_MULTIPLIER
from .trading_config import TradingConfig
from coinbase_advanced_trader.logger import logger


class EnhancedRESTClient(RESTClient):
    """Enhanced REST client with additional trading functionalities."""

    def __init__(self, api_key: str, api_secret: str, **kwargs: Any) -> None:
        """
        Initialize the EnhancedRESTClient.

        Args:
            api_key: The API key for authentication.
            api_secret: The API secret for authentication.
            **kwargs: Additional keyword arguments for RESTClient.
        """
        super().__init__(api_key=api_key, api_secret=api_secret, **kwargs)
        self._price_service = PriceService(self)
        self._order_service = OrderService(self, self._price_service)
        self._config = TradingConfig()
        self._fear_and_greed_strategy = FearAndGreedStrategy(
            self._order_service, self._price_service, self._config
        )

    def update_fgi_schedule(self, new_schedule):
        """
        Update the Fear and Greed Index trading schedule.

        Args:
            new_schedule (List[Dict]): The new schedule to be set.

        Raises:
            ValueError: If the provided schedule is invalid.

        Returns:
            bool: True if the schedule was successfully updated, False otherwise.

        Example:
            >>> client = EnhancedRESTClient(api_key, api_secret)
            >>> new_schedule = [
            ...     {'threshold': 20, 'factor': 1.2, 'action': 'buy'},
            ...     {'threshold': 80, 'factor': 0.8, 'action': 'sell'}
            ... ]
            >>> client.update_fgi_schedule(new_schedule)
            True
        """
        try:
            if self._config.validate_schedule(new_schedule):
                self._config.update_fgi_schedule(new_schedule)
                logger.info("FGI schedule successfully updated.")
                return True
            else:
                logger.warning("Invalid FGI schedule provided. Update rejected.")
                return False
        except ValueError as e:
            logger.error(f"Failed to update FGI schedule: {str(e)}")
            raise

    def get_fgi_schedule(self) -> List[Dict[str, Any]]:
        """
        Get the current Fear and Greed Index schedule.

        Returns:
            The current FGI schedule.
        """
        return self._config.get_fgi_schedule()
    
    def validate_fgi_schedule(self, schedule: List[Dict[str, Any]]) -> bool:
        """
        Validate a Fear and Greed Index trading schedule without updating it.

        Args:
            schedule (List[Dict[str, Any]]): The schedule to validate.

        Returns:
            bool: True if the schedule is valid, False otherwise.

        Example:
            >>> client = EnhancedRESTClient(api_key, api_secret)
            >>> schedule = [
            ...     {'threshold': 20, 'factor': 1.2, 'action': 'buy'},
            ...     {'threshold': 80, 'factor': 0.8, 'action': 'sell'}
            ... ]
            >>> client.validate_fgi_schedule(schedule)
            True
        """
        return self._config.validate_schedule(schedule)

    def fiat_market_buy(self, product_id: str, fiat_amount: str) -> Dict[str, Any]:
        """
        Place a market buy order with fiat currency.

        Args:
            product_id: The product identifier.
            fiat_amount: The amount of fiat currency to spend.

        Returns:
            The result of the market buy order.
        """
        return self._order_service.fiat_market_buy(product_id, fiat_amount)

    def fiat_market_sell(self, product_id: str, fiat_amount: str) -> Dict[str, Any]:
        """
        Place a market sell order with fiat currency.

        Args:
            product_id: The product identifier.
            fiat_amount: The amount of fiat currency to receive.

        Returns:
            The result of the market sell order.
        """
        return self._order_service.fiat_market_sell(product_id, fiat_amount)

    def fiat_limit_buy(
        self,
        product_id: str,
        fiat_amount: str,
        price_multiplier: float = BUY_PRICE_MULTIPLIER
    ) -> Dict[str, Any]:
        """
        Place a limit buy order with fiat currency.

        Args:
            product_id: The product identifier.
            fiat_amount: The amount of fiat currency to spend.
            price_multiplier: The price multiplier for the limit order.

        Returns:
            The result of the limit buy order.
        """
        return self._order_service.fiat_limit_buy(
            product_id, fiat_amount, price_multiplier
        )

    def fiat_limit_sell(
        self,
        product_id: str,
        fiat_amount: str,
        price_multiplier: float = SELL_PRICE_MULTIPLIER
    ) -> Dict[str, Any]:
        """
        Place a limit sell order with fiat currency.

        Args:
            product_id: The product identifier.
            fiat_amount: The amount of fiat currency to receive.
            price_multiplier: The price multiplier for the limit order.

        Returns:
            The result of the limit sell order.
        """
        return self._order_service.fiat_limit_sell(
            product_id, fiat_amount, price_multiplier
        )

    def trade_based_on_fgi(
        self,
        product_id: str,
        fiat_amount: str,
        schedule: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a complex trade based on the Fear and Greed Index.

        Args:
            product_id: The product identifier.
            fiat_amount: The amount of fiat currency to trade.
            schedule: The trading schedule, if any.

        Returns:
            The result of the trade execution.
        """
        return self._fear_and_greed_strategy.execute_trade(
            product_id, fiat_amount
        )
