# Ordered Group Effect Stack

This example applies three named Filters to one composited Group.

```xml
<Group effects={["stack_soft_blur", "stack_color_grade", "stack_opacity"]}>
  ...
</Group>
```

The filters execute from left to right. The current GPU-native Group stack supports Blur, ColorMatrix, and Opacity steps.
