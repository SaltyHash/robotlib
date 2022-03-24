from typing import List
from unittest import TestCase


class RobotlibTestCase(TestCase):
    def assert_list_almost_equal(
            self,
            expected: List[float],
            actual: List[float],
            places: int = 7
    ) -> None:
        if len(expected) != len(actual):
            raise AssertionError(
                f'List lengths do not match: '
                f'len(expected) = {len(expected)}; '
                f'len(actual) = {len(actual)}.'
            )

        matches = []

        for i, (expected_sample, actual_sample) in enumerate(
                zip(expected, actual)):
            try:
                self.assertAlmostEqual(
                    expected_sample,
                    actual_sample,
                    places=places
                )
                matches.append(True)
            except AssertionError:
                matches.append(False)

        if all(matches):
            return

        lines = [
            f'Lists are not the same to {places} decimal places:',
            f'',
            f'        <expected> ?= <actual>'
        ]

        for i, (match, expected_sample, actual_sample) in enumerate(zip(
            matches, expected, actual
        )):
            line = f'[{i}]  '
            line += '   ' if match else '*  '
            line += f'{expected_sample:.{places}f} '
            line += '==' if match else '!='
            line += f' {actual_sample:.{places}f}'
            lines.append(line)

        message = '\n'.join(lines)
        raise AssertionError(message)
